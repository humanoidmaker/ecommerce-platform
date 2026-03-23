"""Seller order management — list, confirm, ship, track."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, require_seller
from app.models.order_item import OrderItem
from app.models.order import Order
from app.services import order_service, seller_service, shipment_service, inventory_service

router = APIRouter(prefix="/seller/orders", tags=["seller-orders"])


@router.get("")
async def list_seller_orders(user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    seller = await seller_service.get_seller_by_user(db, user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    items = (await db.execute(select(OrderItem).where(OrderItem.seller_id == seller.id).order_by(OrderItem.created_at.desc()).limit(50))).scalars().all()
    return [{"id": str(i.id), "order_id": str(i.order_id), "product_title": i.product_title_snapshot, "quantity": i.quantity, "total_price": str(i.total_price), "status": i.status} for i in items]


@router.post("/{item_id}/confirm")
async def confirm_item(item_id: uuid.UUID, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    item = (await db.execute(select(OrderItem).where(OrderItem.id == item_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        await order_service.update_item_status(db, item, "processing")
        return {"message": "Item confirmed"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{item_id}/ship")
async def ship_item(item_id: uuid.UUID, carrier: str = "internal", user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    item = (await db.execute(select(OrderItem).where(OrderItem.id == item_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    seller = await seller_service.get_seller_by_user(db, user.id)
    shipment = await shipment_service.create_shipment(db, item.order_id, seller.id, carrier)
    item.tracking_number = shipment.tracking_number
    await order_service.update_item_status(db, item, "shipped")
    await inventory_service.deduct_stock(db, item.product_id, item.variant_id, item.quantity)
    return {"message": "Shipped", "tracking_number": shipment.tracking_number}


@router.post("/{item_id}/deliver")
async def deliver_item(item_id: uuid.UUID, user: CurrentUser = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    item = (await db.execute(select(OrderItem).where(OrderItem.id == item_id))).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await order_service.update_item_status(db, item, "delivered")
    return {"message": "Marked delivered"}
