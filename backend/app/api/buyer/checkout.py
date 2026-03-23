"""Buyer checkout API — address, shipping, payment, place order."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.services import cart_service, checkout_service
from app.services.checkout_service import CheckoutError
from app.services.shipping_calculator import get_all_shipping_options
from decimal import Decimal

router = APIRouter(prefix="/checkout", tags=["checkout"])


class CheckoutRequest(BaseModel):
    shipping_address: dict
    billing_address: dict
    shipping_method: str = "standard"
    payment_method: str = "card"


class ConfirmPaymentRequest(BaseModel):
    order_id: uuid.UUID
    payment_id: uuid.UUID


@router.get("/shipping-options")
async def shipping_options(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cart = await cart_service.get_or_create_cart(db, user_id=user.id)
    return get_all_shipping_options(Decimal("1.0"), cart.subtotal)


@router.post("/place-order")
async def place_order(body: CheckoutRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        cart = await cart_service.get_or_create_cart(db, user_id=user.id)
        result = await checkout_service.checkout(db, user.id, cart, body.shipping_address, body.billing_address, body.shipping_method, body.payment_method)
        return {
            "order_id": str(result["order"].id),
            "order_number": result["order"].order_number,
            "payment_id": str(result["payment"].id),
            "payment_gateway_id": result["payment"].payment_gateway_id,
            "grand_total": str(result["order"].grand_total),
            "shipping": result["shipping"],
        }
    except CheckoutError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/confirm-payment")
async def confirm_payment(body: ConfirmPaymentRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await checkout_service.confirm_checkout(db, body.order_id, body.payment_id, force_success=True)
        return {
            "success": result["success"],
            "order_status": result["order"].status,
            "payment_status": result["payment"].status,
            "order_number": result["order"].order_number,
        }
    except CheckoutError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
