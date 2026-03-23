"""Review service — submit, edit, respond, helpful votes, rating recalculation."""
from __future__ import annotations
import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review
from app.models.review_helpful import ReviewHelpful
from app.models.order_item import OrderItem
from app.models.product import Product


class ReviewError(Exception):
    pass


async def create_review(db: AsyncSession, product_id: uuid.UUID, buyer_id: uuid.UUID,
                        order_item_id: uuid.UUID, rating: int, title: Optional[str] = None,
                        body: Optional[str] = None, images_json: Optional[list] = None) -> Review:
    if rating < 1 or rating > 5:
        raise ReviewError("Rating must be 1-5")

    # Check order item is delivered
    oi = (await db.execute(select(OrderItem).where(OrderItem.id == order_item_id))).scalar_one_or_none()
    if not oi or oi.status != "delivered":
        raise ReviewError("Can only review delivered items")

    # Check not already reviewed
    existing = (await db.execute(select(Review).where(Review.order_item_id == order_item_id, Review.buyer_id == buyer_id))).scalar_one_or_none()
    if existing:
        raise ReviewError("Already reviewed this item")

    review = Review(
        product_id=product_id, buyer_id=buyer_id, order_item_id=order_item_id,
        rating=rating, title=title, body=body, images_json=images_json,
        is_verified_purchase=True,
    )
    db.add(review)
    await db.flush()

    await _recalculate_product_rating(db, product_id)
    return review


async def update_review(db: AsyncSession, review: Review, rating: Optional[int] = None,
                        title: Optional[str] = None, body: Optional[str] = None) -> Review:
    if rating is not None:
        review.rating = rating
    if title is not None:
        review.title = title
    if body is not None:
        review.body = body
    await db.flush()
    await _recalculate_product_rating(db, review.product_id)
    return review


async def add_seller_response(db: AsyncSession, review: Review, response: str) -> Review:
    from datetime import datetime, timezone
    review.seller_response = response
    review.seller_responded_at = datetime.now(timezone.utc)
    await db.flush()
    return review


async def toggle_helpful(db: AsyncSession, review_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Toggle helpful vote. Returns True if added, False if removed."""
    existing = (await db.execute(select(ReviewHelpful).where(ReviewHelpful.review_id == review_id, ReviewHelpful.user_id == user_id))).scalar_one_or_none()
    review = (await db.execute(select(Review).where(Review.id == review_id))).scalar_one_or_none()

    if existing:
        await db.delete(existing)
        if review:
            review.helpful_count = max(0, review.helpful_count - 1)
        await db.flush()
        return False
    else:
        db.add(ReviewHelpful(review_id=review_id, user_id=user_id))
        if review:
            review.helpful_count += 1
        await db.flush()
        return True


async def list_product_reviews(db: AsyncSession, product_id: uuid.UUID, offset: int = 0, limit: int = 20) -> tuple[list[Review], int]:
    q = select(Review).where(Review.product_id == product_id, Review.is_hidden == False)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
    items = (await db.execute(q.order_by(Review.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def get_rating_distribution(db: AsyncSession, product_id: uuid.UUID) -> dict:
    dist = {}
    for star in range(1, 6):
        count = (await db.execute(select(func.count()).where(Review.product_id == product_id, Review.rating == star, Review.is_hidden == False))).scalar() or 0
        dist[star] = count
    return dist


async def _recalculate_product_rating(db: AsyncSession, product_id: uuid.UUID) -> None:
    avg = (await db.execute(select(func.avg(Review.rating)).where(Review.product_id == product_id, Review.is_hidden == False))).scalar()
    count = (await db.execute(select(func.count()).where(Review.product_id == product_id, Review.is_hidden == False))).scalar() or 0
    product = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
    if product:
        product.average_rating = Decimal(str(round(avg, 2))) if avg else Decimal("0.00")
        product.review_count = count
    await db.flush()
