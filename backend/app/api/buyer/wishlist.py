"""Buyer wishlist API."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.wishlist import Wishlist

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("")
async def list_wishlist(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items = (await db.execute(select(Wishlist).where(Wishlist.user_id == user.id).order_by(Wishlist.created_at.desc()))).scalars().all()
    return [{"product_id": str(w.product_id), "created_at": w.created_at.isoformat()} for w in items]


@router.post("/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(product_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Wishlist).where(Wishlist.user_id == user.id, Wishlist.product_id == product_id))).scalar_one_or_none()
    if existing:
        return {"message": "Already in wishlist"}
    db.add(Wishlist(user_id=user.id, product_id=product_id))
    await db.flush()
    return {"message": "Added to wishlist"}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(product_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Wishlist).where(Wishlist.user_id == user.id, Wishlist.product_id == product_id))
    await db.flush()
