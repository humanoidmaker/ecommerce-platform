"""Cart service — THE most complex service. Real-time validation, guest merge, coupon logic."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.coupon import Coupon
from app.services.pricing_service import get_item_price, calc_line_total, calc_cart_totals
from app.services.inventory_service import get_available_stock
from app.utils.money import money
from app.config import get_settings


class CartError(Exception):
    pass


async def get_or_create_cart(db: AsyncSession, user_id: Optional[uuid.UUID] = None, session_id: Optional[str] = None) -> Cart:
    """Get active cart or create new one."""
    if user_id:
        result = await db.execute(select(Cart).where(Cart.user_id == user_id, Cart.status == "active"))
    elif session_id:
        result = await db.execute(select(Cart).where(Cart.session_id == session_id, Cart.status == "active"))
    else:
        raise CartError("Must provide user_id or session_id")

    cart = result.scalar_one_or_none()
    if not cart:
        settings = get_settings()
        from app.utils.time_utils import hours_from_now
        cart = Cart(user_id=user_id, session_id=session_id, expires_at=hours_from_now(settings.cart_expiry_hours))
        db.add(cart)
        await db.flush()
    return cart


async def add_item(db: AsyncSession, cart: Cart, product_id: uuid.UUID, variant_id: Optional[uuid.UUID] = None, quantity: int = 1) -> CartItem:
    """Add item to cart with validation."""
    # Validate product
    product = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
    if not product or product.status != "active":
        raise CartError("Product not available")

    # Validate variant if specified
    variant = None
    if variant_id:
        variant = (await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))).scalar_one_or_none()
        if not variant or not variant.is_active:
            raise CartError("Variant not available")
    elif product.has_variants:
        raise CartError("Product requires variant selection")

    # Check stock
    available = await get_available_stock(db, product_id, variant_id)
    if quantity > available:
        raise CartError(f"Only {available} available")

    # Check if already in cart
    existing = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id, CartItem.variant_id == variant_id)
    )
    item = existing.scalar_one_or_none()

    unit_price = get_item_price(product.price, variant.price if variant else None)

    if item:
        new_qty = item.quantity + quantity
        if new_qty > available:
            raise CartError(f"Only {available} available (already {item.quantity} in cart)")
        item.quantity = new_qty
        item.unit_price = unit_price
        item.total_price = calc_line_total(unit_price, new_qty)
    else:
        item = CartItem(
            cart_id=cart.id, product_id=product_id, variant_id=variant_id,
            quantity=quantity, unit_price=unit_price, total_price=calc_line_total(unit_price, quantity),
        )
        db.add(item)

    await _recalculate_cart(db, cart)
    return item


async def update_item_quantity(db: AsyncSession, cart: Cart, item_id: uuid.UUID, quantity: int) -> CartItem:
    """Update cart item quantity."""
    if quantity < 1:
        raise CartError("Quantity must be at least 1")

    item = (await db.execute(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))).scalar_one_or_none()
    if not item:
        raise CartError("Item not in cart")

    available = await get_available_stock(db, item.product_id, item.variant_id)
    if quantity > available:
        raise CartError(f"Only {available} available")

    item.quantity = quantity
    item.total_price = calc_line_total(item.unit_price, quantity)
    await _recalculate_cart(db, cart)
    return item


async def remove_item(db: AsyncSession, cart: Cart, item_id: uuid.UUID) -> None:
    await db.execute(delete(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    await _recalculate_cart(db, cart)


async def get_cart_with_validation(db: AsyncSession, cart: Cart) -> dict:
    """Get cart contents with real-time price/stock validation."""
    items_result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    items = list(items_result.scalars().all())

    warnings = []
    valid_items = []

    for item in items:
        product = (await db.execute(select(Product).where(Product.id == item.product_id))).scalar_one_or_none()
        if not product or product.status != "active":
            warnings.append({"item_id": str(item.id), "type": "removed", "message": f"'{product.title if product else 'Product'}' is no longer available"})
            await db.delete(item)
            continue

        variant = None
        if item.variant_id:
            variant = (await db.execute(select(ProductVariant).where(ProductVariant.id == item.variant_id))).scalar_one_or_none()

        # Check price change
        current_price = get_item_price(product.price, variant.price if variant else None)
        if current_price != item.unit_price:
            warnings.append({"item_id": str(item.id), "type": "price_changed", "message": f"Price updated from ${item.unit_price} to ${current_price}", "old_price": str(item.unit_price), "new_price": str(current_price)})
            item.unit_price = current_price
            item.total_price = calc_line_total(current_price, item.quantity)

        # Check stock
        available = await get_available_stock(db, item.product_id, item.variant_id)
        if item.quantity > available:
            if available == 0:
                warnings.append({"item_id": str(item.id), "type": "out_of_stock", "message": f"'{product.title}' is out of stock"})
                await db.delete(item)
                continue
            warnings.append({"item_id": str(item.id), "type": "stock_reduced", "message": f"Quantity reduced to {available}"})
            item.quantity = available
            item.total_price = calc_line_total(item.unit_price, available)

        valid_items.append({"item": item, "product": product, "variant": variant})

    await _recalculate_cart(db, cart)

    return {"cart": cart, "items": valid_items, "warnings": warnings}


async def apply_coupon(db: AsyncSession, cart: Cart, code: str, user_id: uuid.UUID) -> Cart:
    """Apply coupon to cart."""
    from app.services.coupon_service import validate_coupon, CouponError
    try:
        coupon = await validate_coupon(db, code, user_id, cart.subtotal)
    except CouponError as e:
        raise CartError(str(e))
    cart.coupon_id = coupon.id
    await _recalculate_cart(db, cart)
    return cart


async def remove_coupon(db: AsyncSession, cart: Cart) -> Cart:
    cart.coupon_id = None
    await _recalculate_cart(db, cart)
    return cart


async def merge_guest_cart(db: AsyncSession, user_id: uuid.UUID, session_id: str) -> Optional[Cart]:
    """Merge guest cart into user cart on login."""
    guest_cart = (await db.execute(select(Cart).where(Cart.session_id == session_id, Cart.status == "active"))).scalar_one_or_none()
    if not guest_cart:
        return None

    user_cart = await get_or_create_cart(db, user_id=user_id)

    # Move items from guest to user cart
    guest_items = (await db.execute(select(CartItem).where(CartItem.cart_id == guest_cart.id))).scalars().all()
    for gi in guest_items:
        existing = (await db.execute(
            select(CartItem).where(CartItem.cart_id == user_cart.id, CartItem.product_id == gi.product_id, CartItem.variant_id == gi.variant_id)
        )).scalar_one_or_none()
        if existing:
            existing.quantity += gi.quantity
            existing.total_price = calc_line_total(existing.unit_price, existing.quantity)
        else:
            gi.cart_id = user_cart.id

    guest_cart.status = "converted"
    await _recalculate_cart(db, user_cart)
    return user_cart


async def _recalculate_cart(db: AsyncSession, cart: Cart) -> None:
    """Recalculate cart totals."""
    items_result = await db.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    items = list(items_result.scalars().all())

    if not items:
        cart.item_count = 0
        cart.subtotal = Decimal("0.00")
        cart.discount_total = Decimal("0.00")
        cart.tax_total = Decimal("0.00")
        cart.shipping_total = Decimal("0.00")
        cart.grand_total = Decimal("0.00")
        await db.flush()
        return

    # Build pricing items
    pricing_items = []
    for item in items:
        product = (await db.execute(select(Product).where(Product.id == item.product_id))).scalar_one_or_none()
        tax_rate = product.tax_rate if product else Decimal("0.08")
        pricing_items.append({"unit_price": item.unit_price, "quantity": item.quantity, "tax_rate": tax_rate})

    # Get coupon data
    coupon_data = None
    if cart.coupon_id:
        coupon = (await db.execute(select(Coupon).where(Coupon.id == cart.coupon_id))).scalar_one_or_none()
        if coupon:
            coupon_data = {"type": coupon.type, "value": coupon.value, "min_order": coupon.min_order_amount, "max_discount": coupon.max_discount_amount}

    totals = calc_cart_totals(pricing_items, coupon_data)
    cart.item_count = totals["item_count"]
    cart.subtotal = totals["subtotal"]
    cart.discount_total = totals["discount_total"]
    cart.tax_total = totals["tax_total"]
    cart.shipping_total = totals["shipping_total"]
    cart.grand_total = totals["grand_total"]
    cart.updated_at = datetime.now(timezone.utc)
    await db.flush()
