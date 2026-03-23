"""Order lifecycle — create, status transitions, cancel, per-item tracking."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.order import Order
from app.models.order_item import OrderItem
from app.utils.order_number import generate_order_number
from app.utils.money import money

# Valid order status transitions
ORDER_TRANSITIONS = {
    "pending_payment": {"confirmed", "cancelled"},
    "confirmed": {"processing", "cancelled"},
    "processing": {"partially_shipped", "shipped", "cancelled"},
    "partially_shipped": {"shipped"},
    "shipped": {"partially_delivered", "delivered"},
    "partially_delivered": {"delivered"},
    "delivered": {"completed", "refund_requested"},
    "completed": {},
    "cancelled": {},
    "refund_requested": {"refunded"},
    "refunded": {},
}

ITEM_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"processing", "cancelled"},
    "processing": {"shipped", "cancelled"},
    "shipped": {"delivered", "returned"},
    "delivered": {"returned", "refunded"},
    "cancelled": {},
    "returned": {"refunded"},
    "refunded": {},
}


async def create_order(db: AsyncSession, buyer_id: uuid.UUID, cart_items: list[dict],
                       shipping_address: dict, billing_address: dict,
                       subtotal: Decimal, discount_total: Decimal, tax_total: Decimal,
                       shipping_total: Decimal, grand_total: Decimal,
                       coupon_id: Optional[uuid.UUID] = None, coupon_code: Optional[str] = None) -> Order:
    """Create order with items split by seller."""
    order = Order(
        order_number=generate_order_number(), buyer_id=buyer_id,
        shipping_address_json=shipping_address, billing_address_json=billing_address,
        subtotal=subtotal, discount_total=discount_total, tax_total=tax_total,
        shipping_total=shipping_total, grand_total=grand_total,
        coupon_id=coupon_id, coupon_code=coupon_code,
        status="pending_payment", payment_status="pending",
    )
    db.add(order)
    await db.flush()

    # Create order items
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id, seller_id=item["seller_id"],
            product_id=item["product_id"], variant_id=item.get("variant_id"),
            product_title_snapshot=item["title"], variant_name_snapshot=item.get("variant_name"),
            product_image_snapshot=item.get("image_url"), sku=item.get("sku"),
            quantity=item["quantity"], unit_price=item["unit_price"],
            total_price=item["total_price"], tax_amount=item.get("tax_amount", Decimal("0.00")),
            commission_rate=item["commission_rate"],
            commission_amount=money(Decimal(str(item["total_price"])) * Decimal(str(item["commission_rate"]))),
            status="pending",
        )
        db.add(order_item)

    await db.flush()
    return order


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> Optional[Order]:
    result = await db.execute(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def get_order_by_number(db: AsyncSession, order_number: str) -> Optional[Order]:
    result = await db.execute(select(Order).options(selectinload(Order.items)).where(Order.order_number == order_number))
    return result.scalar_one_or_none()


async def list_buyer_orders(db: AsyncSession, buyer_id: uuid.UUID, offset: int = 0, limit: int = 20) -> tuple[list[Order], int]:
    q = select(Order).where(Order.buyer_id == buyer_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
    items = (await db.execute(q.options(selectinload(Order.items)).order_by(Order.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def confirm_order(db: AsyncSession, order: Order) -> Order:
    """Confirm order after successful payment."""
    order.status = "confirmed"
    order.payment_status = "paid"
    # Confirm all items
    for item in (await _get_items(db, order.id)):
        item.status = "confirmed"
    await db.flush()
    return order


async def cancel_order(db: AsyncSession, order: Order, cancelled_by: uuid.UUID, reason: str = "") -> Order:
    """Cancel order. Only allowed if not yet shipped."""
    if order.status not in ("pending_payment", "confirmed", "processing"):
        raise ValueError(f"Cannot cancel order in state: {order.status}")

    order.status = "cancelled"
    order.cancellation_reason = reason
    order.cancelled_by = cancelled_by
    order.cancelled_at = datetime.now(timezone.utc)

    for item in (await _get_items(db, order.id)):
        if item.status in ("pending", "confirmed", "processing"):
            item.status = "cancelled"

    await db.flush()
    return order


async def update_item_status(db: AsyncSession, item: OrderItem, new_status: str) -> OrderItem:
    valid = ITEM_TRANSITIONS.get(item.status, set())
    if new_status not in valid:
        raise ValueError(f"Cannot transition item from {item.status} to {new_status}")
    item.status = new_status
    if new_status == "shipped":
        item.shipped_at = datetime.now(timezone.utc)
    elif new_status == "delivered":
        item.delivered_at = datetime.now(timezone.utc)
    await db.flush()

    # Check if all items have same status → update order
    order = await get_order(db, item.order_id)
    if order:
        await _sync_order_status(db, order)
    return item


async def _get_items(db: AsyncSession, order_id: uuid.UUID) -> list[OrderItem]:
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    return list(result.scalars().all())


async def _sync_order_status(db: AsyncSession, order: Order) -> None:
    """Sync order status based on item statuses."""
    items = await _get_items(db, order.id)
    if not items:
        return

    statuses = {i.status for i in items}
    if statuses == {"delivered"}:
        order.status = "delivered"
    elif statuses == {"shipped"} or statuses == {"delivered", "shipped"}:
        order.status = "shipped"
    elif "shipped" in statuses:
        order.status = "partially_shipped"
    elif statuses == {"cancelled"}:
        order.status = "cancelled"
    elif statuses == {"refunded"}:
        order.status = "refunded"
    await db.flush()
