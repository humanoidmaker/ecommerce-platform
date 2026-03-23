"""Buyer product detail API."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import catalog_service, product_service
from app.services.shipping_calculator import get_all_shipping_options, estimate_delivery_date
from decimal import Decimal

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{slug}")
async def product_detail(slug: str, db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product_by_slug(db, slug)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    detail = await catalog_service.get_product_detail(db, product.id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    p = detail["product"]
    weight = p.weight_kg or Decimal("0.5")
    shipping_options = get_all_shipping_options(weight, p.price)

    return {
        "product": _serialize_product(p),
        "variants": [_serialize_variant(v) for v in (p.variants or [])],
        "images": [_serialize_image(i) for i in (p.images or [])],
        "attributes": [{"name": a.name, "values": a.values_json} for a in (p.attributes or [])],
        "seller": _serialize_seller(detail["seller"]) if detail["seller"] else None,
        "rating_distribution": detail["rating_distribution"],
        "shipping_options": shipping_options,
        "related_products": [_serialize_product_brief(rp) for rp in detail.get("related_products", [])],
    }


def _serialize_product(p) -> dict:
    return {
        "id": str(p.id), "title": p.title, "slug": p.slug,
        "description": p.description, "short_description": p.short_description,
        "price": str(p.price), "compare_at_price": str(p.compare_at_price) if p.compare_at_price else None,
        "currency": p.currency, "brand": p.brand, "tags": p.tags,
        "condition": p.condition, "is_digital": p.is_digital,
        "average_rating": str(p.average_rating), "review_count": p.review_count,
        "total_sold": p.total_sold, "view_count": p.view_count,
        "has_variants": p.has_variants, "weight_kg": str(p.weight_kg) if p.weight_kg else None,
    }


def _serialize_variant(v) -> dict:
    return {
        "id": str(v.id), "name": v.name, "sku": v.sku,
        "attributes": v.attributes_json, "price": str(v.price) if v.price else None,
        "stock_quantity": v.stock_quantity, "reserved_quantity": v.reserved_quantity,
        "available": max(0, v.stock_quantity - v.reserved_quantity),
        "is_active": v.is_active, "image_id": str(v.image_id) if v.image_id else None,
    }


def _serialize_image(i) -> dict:
    return {"id": str(i.id), "url": i.url, "thumbnail_url": i.thumbnail_url, "alt_text": i.alt_text, "is_primary": i.is_primary, "sort_order": i.sort_order}


def _serialize_seller(s) -> dict:
    return {"id": str(s.id), "store_name": s.store_name, "store_slug": s.store_slug, "logo_url": s.logo_url, "average_rating": str(s.average_rating), "review_count": s.review_count, "is_verified": s.is_verified}


def _serialize_product_brief(p) -> dict:
    img = next((i for i in (p.images or []) if i.is_primary), None) or (p.images[0] if p.images else None)
    return {"id": str(p.id), "title": p.title, "slug": p.slug, "price": str(p.price), "compare_at_price": str(p.compare_at_price) if p.compare_at_price else None, "average_rating": str(p.average_rating), "image_url": img.url if img else None}
