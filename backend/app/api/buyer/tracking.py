"""Buyer shipment tracking API."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.services import shipment_service

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.get("/{order_id}")
async def get_tracking(order_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    shipments = await shipment_service.get_shipments_for_order(db, order_id)
    if not shipments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No shipments found")
    return [{
        "id": str(s.id), "tracking_number": s.tracking_number, "carrier": s.carrier,
        "status": s.status, "estimated_delivery": s.estimated_delivery_date.isoformat() if s.estimated_delivery_date else None,
        "actual_delivery": s.actual_delivery_date.isoformat() if s.actual_delivery_date else None,
        "events": s.tracking_events_json or [],
    } for s in shipments]
