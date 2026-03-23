"""Seller analytics and payouts API."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, require_seller
from app.services import seller_service, commission_service

router = APIRouter(prefix="/seller", tags=["seller-analytics"])


@router.get("/dashboard")
async def seller_dashboard(user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    seller = await seller_service.get_seller_by_user(db, user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    commission_summary = await commission_service.get_seller_commission_summary(db, seller.id)
    return {
        "store_name": seller.store_name,
        "total_orders": seller.total_orders,
        "total_revenue": str(seller.total_revenue),
        "total_products": seller.total_products,
        "average_rating": str(seller.average_rating),
        "review_count": seller.review_count,
        "commission": commission_summary,
    }


@router.get("/payouts")
async def list_payouts(user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    seller = await seller_service.get_seller_by_user(db, user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    payouts = await commission_service.list_seller_payouts(db, seller.id)
    return [{"id": str(p.id), "amount": str(p.amount), "status": p.status, "period_start": p.period_start.isoformat(), "period_end": p.period_end.isoformat(), "items_count": p.items_count, "reference": p.payout_reference} for p in payouts]
