"""Buyer reviews API."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.services.review_service import create_review, toggle_helpful, list_product_reviews, ReviewError

router = APIRouter(prefix="/reviews", tags=["reviews"])


class WriteReviewRequest(BaseModel):
    product_id: uuid.UUID
    order_item_id: uuid.UUID
    rating: int = Field(ge=1, le=5)
    title: str | None = None
    body: str | None = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def write_review(body: WriteReviewRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        review = await create_review(db, body.product_id, user.id, body.order_item_id, body.rating, body.title, body.body)
        return {"id": str(review.id), "rating": review.rating}
    except ReviewError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/product/{product_id}")
async def product_reviews(product_id: uuid.UUID, page: int = 1, db: AsyncSession = Depends(get_db)):
    reviews, total = await list_product_reviews(db, product_id, (page - 1) * 10, 10)
    return {"items": [{"id": str(r.id), "rating": r.rating, "title": r.title, "body": r.body, "helpful_count": r.helpful_count, "is_verified": r.is_verified_purchase, "created_at": r.created_at.isoformat()} for r in reviews], "total": total}


@router.post("/{review_id}/helpful")
async def mark_helpful(review_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    added = await toggle_helpful(db, review_id, user.id)
    return {"helpful": added}
