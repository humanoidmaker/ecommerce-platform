"""Seller store profile API."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, require_seller
from app.services import seller_service

router = APIRouter(prefix="/seller/store", tags=["seller"])


class UpdateStoreRequest(BaseModel):
    store_name: str | None = None
    store_description: str | None = None
    return_policy_text: str | None = None
    shipping_policy_text: str | None = None


@router.get("")
async def get_store(user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    seller = await seller_service.get_seller_by_user(db, user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
    return {"id": str(seller.id), "store_name": seller.store_name, "store_slug": seller.store_slug,
            "store_description": seller.store_description, "logo_url": seller.logo_url, "banner_url": seller.banner_url,
            "application_status": seller.application_status, "is_verified": seller.is_verified,
            "commission_rate": str(seller.commission_rate), "total_orders": seller.total_orders,
            "total_revenue": str(seller.total_revenue), "average_rating": str(seller.average_rating)}


@router.patch("")
async def update_store(body: UpdateStoreRequest, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    seller = await seller_service.get_seller_by_user(db, user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    updated = await seller_service.update_store(db, seller, **body.model_dump(exclude_none=True))
    return {"message": "Store updated", "store_name": updated.store_name}
