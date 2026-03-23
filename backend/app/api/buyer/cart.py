"""Buyer cart API."""
from __future__ import annotations
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user, get_optional_user
from app.services import cart_service
from app.services.cart_service import CartError

router = APIRouter(prefix="/cart", tags=["cart"])


class AddItemRequest(BaseModel):
    product_id: uuid.UUID
    variant_id: Optional[uuid.UUID] = None
    quantity: int = Field(1, ge=1)


class UpdateQuantityRequest(BaseModel):
    quantity: int = Field(ge=1)


class ApplyCouponRequest(BaseModel):
    code: str


@router.get("")
async def get_cart(user: Optional[CurrentUser] = Depends(get_optional_user), x_session_id: Optional[str] = Header(None),
                   db: AsyncSession = Depends(get_db)):
    cart = await cart_service.get_or_create_cart(db, user_id=user.id if user else None, session_id=x_session_id if not user else None)
    result = await cart_service.get_cart_with_validation(db, cart)
    return _serialize_cart(result)


@router.post("/items")
async def add_item(body: AddItemRequest, user: Optional[CurrentUser] = Depends(get_optional_user),
                   x_session_id: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    try:
        cart = await cart_service.get_or_create_cart(db, user_id=user.id if user else None, session_id=x_session_id if not user else None)
        item = await cart_service.add_item(db, cart, body.product_id, body.variant_id, body.quantity)
        return {"message": "Item added", "item_id": str(item.id)}
    except CartError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/items/{item_id}")
async def update_quantity(item_id: uuid.UUID, body: UpdateQuantityRequest,
                          user: Optional[CurrentUser] = Depends(get_optional_user),
                          x_session_id: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    try:
        cart = await cart_service.get_or_create_cart(db, user_id=user.id if user else None, session_id=x_session_id if not user else None)
        await cart_service.update_item_quantity(db, cart, item_id, body.quantity)
        return {"message": "Updated"}
    except CartError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(item_id: uuid.UUID, user: Optional[CurrentUser] = Depends(get_optional_user),
                      x_session_id: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    cart = await cart_service.get_or_create_cart(db, user_id=user.id if user else None, session_id=x_session_id if not user else None)
    await cart_service.remove_item(db, cart, item_id)


@router.post("/coupon")
async def apply_coupon(body: ApplyCouponRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        cart = await cart_service.get_or_create_cart(db, user_id=user.id)
        await cart_service.apply_coupon(db, cart, body.code, user.id)
        return {"message": "Coupon applied"}
    except CartError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/coupon")
async def remove_coupon(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cart = await cart_service.get_or_create_cart(db, user_id=user.id)
    await cart_service.remove_coupon(db, cart)
    return {"message": "Coupon removed"}


@router.post("/merge")
async def merge_cart(x_session_id: str = Header(...), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await cart_service.merge_guest_cart(db, user.id, x_session_id)
    return {"message": "Cart merged"}


def _serialize_cart(data: dict) -> dict:
    cart = data["cart"]
    return {
        "id": str(cart.id),
        "item_count": cart.item_count,
        "subtotal": str(cart.subtotal),
        "discount_total": str(cart.discount_total),
        "tax_total": str(cart.tax_total),
        "shipping_total": str(cart.shipping_total),
        "grand_total": str(cart.grand_total),
        "items": [{
            "id": str(vi["item"].id),
            "product_id": str(vi["item"].product_id),
            "variant_id": str(vi["item"].variant_id) if vi["item"].variant_id else None,
            "product_title": vi["product"].title,
            "variant_name": vi["variant"].name if vi["variant"] else None,
            "unit_price": str(vi["item"].unit_price),
            "quantity": vi["item"].quantity,
            "total_price": str(vi["item"].total_price),
            "image_url": (vi["product"].images[0].url if vi["product"].images else None) if hasattr(vi["product"], "images") else None,
        } for vi in data["items"]],
        "warnings": data["warnings"],
    }
