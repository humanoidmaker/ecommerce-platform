"""Coupon validation, application, usage tracking."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.coupon import Coupon
from app.models.order import Order
from app.utils.time_utils import utc_now


class CouponError(Exception):
    pass


async def validate_coupon(db: AsyncSession, code: str, user_id: uuid.UUID, subtotal: Decimal,
                          product_ids: Optional[list[uuid.UUID]] = None, category_ids: Optional[list[uuid.UUID]] = None,
                          seller_ids: Optional[list[uuid.UUID]] = None) -> Coupon:
    """Validate coupon and return it. Raises CouponError on failure."""
    result = await db.execute(select(Coupon).where(Coupon.code == code.upper()))
    coupon = result.scalar_one_or_none()

    if not coupon:
        raise CouponError("Invalid coupon code")
    if not coupon.is_active:
        raise CouponError("Coupon is not active")

    now = utc_now()
    if coupon.starts_at and coupon.starts_at > now:
        raise CouponError("Coupon is not yet active")
    if coupon.expires_at and coupon.expires_at < now:
        raise CouponError("Coupon has expired")

    # Usage limits
    if coupon.usage_limit and coupon.usage_count >= coupon.usage_limit:
        raise CouponError("Coupon usage limit reached")

    # Per-user limit
    if coupon.per_user_limit:
        user_usage = (await db.execute(
            select(func.count()).where(Order.buyer_id == user_id, Order.coupon_code == code.upper())
        )).scalar() or 0
        if user_usage >= coupon.per_user_limit:
            raise CouponError("You have already used this coupon the maximum number of times")

    # Min order
    if coupon.min_order_amount and subtotal < coupon.min_order_amount:
        raise CouponError(f"Minimum order amount is ${coupon.min_order_amount}")

    # Scope check
    if coupon.applicable_to != "all" and coupon.applicable_ids_json:
        ids = set(str(i) for i in coupon.applicable_ids_json)
        if coupon.applicable_to == "specific_products" and product_ids:
            if not any(str(pid) in ids for pid in product_ids):
                raise CouponError("Coupon not applicable to items in cart")
        elif coupon.applicable_to == "specific_categories" and category_ids:
            if not any(str(cid) in ids for cid in category_ids):
                raise CouponError("Coupon not applicable to items in cart")
        elif coupon.applicable_to == "specific_sellers" and seller_ids:
            if not any(str(sid) in ids for sid in seller_ids):
                raise CouponError("Coupon not applicable to items in cart")

    return coupon


async def increment_usage(db: AsyncSession, coupon_id: uuid.UUID) -> None:
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if coupon:
        coupon.usage_count += 1
        await db.flush()


async def get_coupon_by_code(db: AsyncSession, code: str) -> Optional[Coupon]:
    result = await db.execute(select(Coupon).where(Coupon.code == code.upper()))
    return result.scalar_one_or_none()
