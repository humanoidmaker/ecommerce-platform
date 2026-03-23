"""Buyer search API — search, autocomplete, filters."""
from __future__ import annotations
import uuid
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search_products(
    q: str = Query(..., min_length=1),
    category_id: Optional[uuid.UUID] = None,
    min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None,
    min_rating: Optional[float] = None,
    brand: Optional[str] = None,
    seller_id: Optional[uuid.UUID] = None,
    condition: Optional[str] = None,
    sort: str = Query("relevance"),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    products, total = await search_service.search_products(
        db, q, category_id, min_price, max_price, min_rating, brand, seller_id, condition,
        sort, (page - 1) * page_size, page_size,
    )

    facets = await search_service.get_facets(db, q, category_id)

    return {
        "query": q,
        "results": [_serialize(p) for p in products],
        "total": total,
        "page": page,
        "facets": facets,
    }


@router.get("/autocomplete")
async def autocomplete(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    return await search_service.autocomplete(db, q)


def _serialize(p) -> dict:
    img = next((i for i in (p.images or []) if i.is_primary), None) or (p.images[0] if p.images else None)
    return {
        "id": str(p.id), "title": p.title, "slug": p.slug,
        "price": str(p.price), "compare_at_price": str(p.compare_at_price) if p.compare_at_price else None,
        "average_rating": str(p.average_rating), "review_count": p.review_count,
        "brand": p.brand, "condition": p.condition,
        "image_url": img.url if img else None,
        "thumbnail_url": img.thumbnail_url if img else None,
    }
