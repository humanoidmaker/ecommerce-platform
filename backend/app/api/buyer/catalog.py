"""Buyer catalog API — home page, category page, product listings."""
from __future__ import annotations
import uuid
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import catalog_service, category_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/home")
async def home_page(db: AsyncSession = Depends(get_db)):
    data = await catalog_service.get_home_page(db)
    return _serialize_home(data)


@router.get("/categories")
async def list_root_categories(db: AsyncSession = Depends(get_db)):
    cats = await category_service.list_categories(db, parent_id=None)
    return [{"id": c.id, "name": c.name, "slug": c.slug, "icon_key": c.icon_key, "product_count": c.product_count} for c in cats]


@router.get("/categories/tree")
async def category_tree(db: AsyncSession = Depends(get_db)):
    return await category_service.get_category_tree(db)


@router.get("/categories/{slug}")
async def category_page(slug: str, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                        sort: str = "newest", min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None,
                        min_rating: Optional[float] = None, db: AsyncSession = Depends(get_db)):
    cat = await category_service.get_category_by_slug(db, slug)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    data = await catalog_service.get_category_page(db, cat.id, (page - 1) * page_size, page_size, sort, min_price, max_price, min_rating)
    return data


@router.get("/categories/{category_id}/breadcrumb")
async def breadcrumb(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await category_service.get_breadcrumb(db, category_id)


def _serialize_home(data: dict) -> dict:
    """Serialize home page data."""
    def _prod(p):
        primary_image = next((i for i in (p.images or []) if i.is_primary), None) or (p.images[0] if p.images else None)
        return {
            "id": str(p.id), "title": p.title, "slug": p.slug, "price": str(p.price),
            "compare_at_price": str(p.compare_at_price) if p.compare_at_price else None,
            "average_rating": str(p.average_rating), "review_count": p.review_count,
            "image_url": primary_image.url if primary_image else None,
            "thumbnail_url": primary_image.thumbnail_url if primary_image else None,
            "is_featured": p.is_featured, "is_bestseller": p.is_bestseller,
        }

    return {
        "featured": [_prod(p) for p in data.get("featured", [])],
        "bestsellers": [_prod(p) for p in data.get("bestsellers", [])],
        "deals": [_prod(p) for p in data.get("deals", [])],
        "new_arrivals": [_prod(p) for p in data.get("new_arrivals", [])],
        "categories": [{"id": str(c.id), "name": c.name, "slug": c.slug, "icon_key": c.icon_key, "product_count": c.product_count} for c in data.get("categories", [])],
    }
