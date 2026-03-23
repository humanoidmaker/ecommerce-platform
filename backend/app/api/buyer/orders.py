"""Buyer orders API — list, detail, cancel."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.services import order_service
from app.utils.pagination import PaginationParams, get_pagination

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
async def list_orders(pagination: PaginationParams = Depends(get_pagination), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    orders, total = await order_service.list_buyer_orders(db, user.id, pagination.offset, pagination.limit)
    return {
        "items": [_serialize_order(o) for o in orders],
        "total": total, "page": pagination.page, "page_size": pagination.page_size,
    }


@router.get("/{order_id}")
async def order_detail(order_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = await order_service.get_order(db, order_id)
    if not order or order.buyer_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return _serialize_order_detail(order)


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    order = await order_service.get_order(db, order_id)
    if not order or order.buyer_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    try:
        await order_service.cancel_order(db, order, user.id, "Cancelled by buyer")
        # Release inventory
        from app.services import inventory_service
        for item in (order.items or []):
            await inventory_service.release_stock(db, item.product_id, item.variant_id, item.quantity)
        return {"message": "Order cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def _serialize_order(o) -> dict:
    return {
        "id": str(o.id), "order_number": o.order_number, "status": o.status,
        "payment_status": o.payment_status, "grand_total": str(o.grand_total),
        "item_count": len(o.items) if o.items else 0,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _serialize_order_detail(o) -> dict:
    return {
        **_serialize_order(o),
        "subtotal": str(o.subtotal), "discount_total": str(o.discount_total),
        "tax_total": str(o.tax_total), "shipping_total": str(o.shipping_total),
        "shipping_address": o.shipping_address_json, "billing_address": o.billing_address_json,
        "coupon_code": o.coupon_code,
        "items": [{
            "id": str(i.id), "product_title": i.product_title_snapshot,
            "variant_name": i.variant_name_snapshot, "image_url": i.product_image_snapshot,
            "sku": i.sku, "quantity": i.quantity,
            "unit_price": str(i.unit_price), "total_price": str(i.total_price),
            "status": i.status, "tracking_number": i.tracking_number,
            "shipped_at": i.shipped_at.isoformat() if i.shipped_at else None,
            "delivered_at": i.delivered_at.isoformat() if i.delivered_at else None,
        } for i in (o.items or [])],
        "cancellation_reason": o.cancellation_reason,
    }
