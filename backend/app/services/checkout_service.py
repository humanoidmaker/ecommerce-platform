"""Checkout service — validate cart, reserve inventory, create order, handle payment."""
from __future__ import annotations
import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.seller import Seller
from app.services import cart_service, inventory_service, order_service, payment_service, pricing_service
from app.services.inventory_service import InsufficientStockError
from app.services.shipping_calculator import calculate_shipping
from app.utils.money import money, calc_tax


class CheckoutError(Exception):
    pass


async def checkout(db: AsyncSession, user_id: uuid.UUID, cart: Cart,
                   shipping_address: dict, billing_address: dict,
                   shipping_method: str = "standard", payment_method: str = "card") -> dict:
    """
    Full checkout flow:
    1. Validate cart (stock, prices, product active)
    2. Reserve inventory
    3. Calculate final totals with shipping
    4. Create order (split items by seller)
    5. Create payment intent
    Returns: {"order": Order, "payment": Payment}
    """
    # 1. Validate cart
    cart_data = await cart_service.get_cart_with_validation(db, cart)
    valid_items = cart_data["items"]

    if not valid_items:
        raise CheckoutError("Cart is empty")

    if cart_data["warnings"]:
        for w in cart_data["warnings"]:
            if w["type"] in ("removed", "out_of_stock"):
                raise CheckoutError(f"Some items are no longer available: {w['message']}")

    # 2. Reserve inventory for each item
    reserved = []
    try:
        for vi in valid_items:
            item = vi["item"]
            await inventory_service.reserve_stock(db, item.product_id, item.variant_id, item.quantity)
            reserved.append((item.product_id, item.variant_id, item.quantity))
    except InsufficientStockError as e:
        # Release all previously reserved
        for pid, vid, qty in reserved:
            await inventory_service.release_stock(db, pid, vid, qty)
        raise CheckoutError(f"Insufficient stock for one or more items") from e

    # 3. Calculate final totals
    total_weight = Decimal("0.00")
    for vi in valid_items:
        product = vi["product"]
        total_weight += (product.weight_kg or Decimal("0.5")) * vi["item"].quantity

    shipping_info = calculate_shipping(shipping_method, total_weight, cart.subtotal)
    shipping_cost = shipping_info["cost"]

    # Apply shipping to coupon if free_shipping
    coupon_code = None
    coupon_id = None
    if cart.coupon_id:
        from app.models.coupon import Coupon
        coupon = (await db.execute(select(Coupon).where(Coupon.id == cart.coupon_id))).scalar_one_or_none()
        if coupon and coupon.type == "free_shipping":
            shipping_cost = Decimal("0.00")
        if coupon:
            coupon_code = coupon.code
            coupon_id = coupon.id

    grand_total = money(cart.subtotal - cart.discount_total + cart.tax_total + shipping_cost)

    # 4. Build order items
    order_items = []
    for vi in valid_items:
        item = vi["item"]
        product = vi["product"]
        variant = vi["variant"]
        seller = (await db.execute(select(Seller).where(Seller.id == product.seller_id))).scalar_one_or_none()
        commission_rate = seller.commission_rate if seller else Decimal("0.15")

        primary_img = None
        if product.images:
            primary_img = next((i for i in product.images if i.is_primary), None) or (product.images[0] if product.images else None)

        order_items.append({
            "seller_id": product.seller_id,
            "product_id": product.id,
            "variant_id": item.variant_id,
            "title": product.title,
            "variant_name": variant.name if variant else None,
            "image_url": primary_img.url if primary_img else None,
            "sku": variant.sku if variant else product.sku,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
            "tax_amount": calc_tax(item.total_price, product.tax_rate),
            "commission_rate": commission_rate,
        })

    # 5. Create order
    order = await order_service.create_order(
        db, user_id, order_items, shipping_address, billing_address,
        cart.subtotal, cart.discount_total, cart.tax_total, shipping_cost, grand_total,
        coupon_id, coupon_code,
    )

    # 6. Create payment intent
    payment = await payment_service.create_payment_intent(db, order.id, grand_total, payment_method=payment_method)

    # 7. Mark cart as converted
    cart.status = "converted"

    # 8. Increment coupon usage
    if coupon_id:
        from app.services.coupon_service import increment_usage
        await increment_usage(db, coupon_id)

    await db.flush()

    return {"order": order, "payment": payment, "shipping": shipping_info}


async def confirm_checkout(db: AsyncSession, order_id: uuid.UUID, payment_id: uuid.UUID,
                           force_success: Optional[bool] = None) -> dict:
    """
    Confirm payment for an order.
    On success: confirm order, update item statuses.
    On failure: cancel order, release inventory.
    """
    payment = await payment_service.confirm_payment(db, payment_id, force_success)
    order = await order_service.get_order(db, order_id)
    if not order:
        raise CheckoutError("Order not found")

    if payment.status == "completed":
        # Success — confirm order
        order = await order_service.confirm_order(db, order)
        return {"order": order, "payment": payment, "success": True}
    else:
        # Failure — cancel and release inventory
        order.status = "cancelled"
        order.payment_status = "failed"
        order.cancellation_reason = "Payment failed"

        items = (await db.execute(select(CartItem).where(CartItem.cart_id == order.id))).scalars().all()
        # Release inventory for each item
        from app.models.order_item import OrderItem
        order_items = (await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))).scalars().all()
        for oi in order_items:
            await inventory_service.release_stock(db, oi.product_id, oi.variant_id, oi.quantity)
            oi.status = "cancelled"

        await db.flush()
        return {"order": order, "payment": payment, "success": False}
