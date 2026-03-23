"""Seller application, store management, verification."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.seller import Seller
from app.models.user import User


async def get_seller(db: AsyncSession, seller_id: uuid.UUID) -> Optional[Seller]:
    return (await db.execute(select(Seller).where(Seller.id == seller_id))).scalar_one_or_none()


async def get_seller_by_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[Seller]:
    return (await db.execute(select(Seller).where(Seller.user_id == user_id))).scalar_one_or_none()


async def get_seller_by_slug(db: AsyncSession, slug: str) -> Optional[Seller]:
    return (await db.execute(select(Seller).where(Seller.store_slug == slug))).scalar_one_or_none()


async def list_sellers(db: AsyncSession, status: Optional[str] = None, offset: int = 0, limit: int = 20) -> tuple[list[Seller], int]:
    q = select(Seller)
    if status:
        q = q.where(Seller.application_status == status)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
    items = (await db.execute(q.order_by(Seller.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def approve_seller(db: AsyncSession, seller: Seller) -> Seller:
    seller.application_status = "approved"
    seller.is_verified = True
    seller.verified_at = datetime.now(timezone.utc)
    # Update user role
    user = (await db.execute(select(User).where(User.id == seller.user_id))).scalar_one_or_none()
    if user:
        user.role = "seller"
    await db.flush()
    return seller


async def reject_seller(db: AsyncSession, seller: Seller, reason: str) -> Seller:
    seller.application_status = "rejected"
    seller.rejection_reason = reason
    await db.flush()
    return seller


async def suspend_seller(db: AsyncSession, seller: Seller) -> Seller:
    seller.application_status = "suspended"
    await db.flush()
    return seller


async def update_store(db: AsyncSession, seller: Seller, **kwargs) -> Seller:
    for key, value in kwargs.items():
        if value is not None and hasattr(seller, key):
            setattr(seller, key, value)
    seller.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return seller


async def update_seller_stats(db: AsyncSession, seller_id: uuid.UUID) -> None:
    """Recalculate seller stats from orders and reviews."""
    from app.models.order_item import OrderItem
    from app.models.review import Review
    from app.models.product import Product

    seller = await get_seller(db, seller_id)
    if not seller:
        return

    # Order stats
    total_orders = (await db.execute(select(func.count(func.distinct(OrderItem.order_id))).where(OrderItem.seller_id == seller_id))).scalar() or 0
    total_revenue = (await db.execute(select(func.coalesce(func.sum(OrderItem.total_price), 0)).where(OrderItem.seller_id == seller_id, OrderItem.status.notin_(["cancelled", "refunded"])))).scalar() or Decimal("0")
    total_products = (await db.execute(select(func.count()).where(Product.seller_id == seller_id, Product.status != "archived"))).scalar() or 0

    # Review stats
    avg_rating = (await db.execute(select(func.avg(Review.rating)).join(Product).where(Product.seller_id == seller_id, Review.is_hidden == False))).scalar()
    review_count = (await db.execute(select(func.count()).select_from(Review).join(Product).where(Product.seller_id == seller_id, Review.is_hidden == False))).scalar() or 0

    seller.total_orders = total_orders
    seller.total_revenue = Decimal(str(total_revenue))
    seller.total_products = total_products
    seller.average_rating = Decimal(str(round(avg_rating, 2))) if avg_rating else Decimal("0.00")
    seller.review_count = review_count
    await db.flush()
