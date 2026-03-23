"""Seller product management API."""
from __future__ import annotations
import uuid
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, require_seller
from app.services import product_service, seller_service, image_service
from app.utils.pagination import PaginationParams, get_pagination

router = APIRouter(prefix="/seller/products", tags=["seller-products"])


class CreateProductRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    price: Decimal = Field(gt=0)
    description: str | None = None
    short_description: str | None = None
    category_id: uuid.UUID | None = None
    brand: str | None = None
    tags: list[str] | None = None
    sku: str | None = None
    weight_kg: Decimal | None = None
    compare_at_price: Decimal | None = None
    cost_price: Decimal | None = None
    condition: str = "new"


class AddVariantRequest(BaseModel):
    name: str
    sku: str
    attributes_json: dict
    price: Decimal | None = None
    stock_quantity: int = 0


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(body: CreateProductRequest, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    seller = await seller_service.get_seller_by_user(db, user.id)
    if not seller or seller.application_status != "approved":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seller not approved")
    product = await product_service.create_product(db, seller.id, body.title, body.price, **body.model_dump(exclude={"title", "price"}))
    return {"id": str(product.id), "title": product.title, "slug": product.slug, "status": product.status}


@router.get("")
async def list_products(status_filter: Optional[str] = None, pagination: PaginationParams = Depends(get_pagination),
                        user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    seller = await seller_service.get_seller_by_user(db, user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    products, total = await product_service.list_products(db, seller_id=seller.id, status=status_filter, offset=pagination.offset, limit=pagination.limit)
    return {"items": [{"id": str(p.id), "title": p.title, "price": str(p.price), "status": p.status, "total_sold": p.total_sold} for p in products], "total": total}


@router.get("/{product_id}")
async def get_product(product_id: uuid.UUID, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"id": str(product.id), "title": product.title, "slug": product.slug, "price": str(product.price),
            "status": product.status, "has_variants": product.has_variants,
            "variants": [{"id": str(v.id), "name": v.name, "sku": v.sku, "price": str(v.price) if v.price else None, "stock_quantity": v.stock_quantity} for v in (product.variants or [])],
            "images": [{"id": str(i.id), "url": i.url, "is_primary": i.is_primary} for i in (product.images or [])]}


@router.patch("/{product_id}")
async def update_product(product_id: uuid.UUID, body: dict, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    updated = await product_service.update_product(db, product, **body)
    return {"message": "Updated", "title": updated.title}


@router.post("/{product_id}/publish")
async def publish_product(product_id: uuid.UUID, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        await product_service.change_status(db, product, "active")
        return {"message": "Published"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{product_id}/variants", status_code=status.HTTP_201_CREATED)
async def add_variant(product_id: uuid.UUID, body: AddVariantRequest, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    variant = await product_service.add_variant(db, product_id, body.name, body.sku, body.attributes_json, body.price, body.stock_quantity)
    return {"id": str(variant.id), "name": variant.name}


@router.post("/{product_id}/duplicate", status_code=status.HTTP_201_CREATED)
async def duplicate_product(product_id: uuid.UUID, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    new = await product_service.duplicate_product(db, product)
    return {"id": str(new.id), "title": new.title}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: uuid.UUID, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await product_service.delete_product(db, product)
