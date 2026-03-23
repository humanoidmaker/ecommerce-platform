"""Buyer address CRUD API."""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.address import Address

router = APIRouter(prefix="/addresses", tags=["addresses"])


class AddressRequest(BaseModel):
    label: str = "Home"
    full_name: str
    phone: str
    address_line1: str
    address_line2: str | None = None
    city: str
    state: str
    postal_code: str
    country: str = "US"
    is_default: bool = False


@router.get("")
async def list_addresses(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items = (await db.execute(select(Address).where(Address.user_id == user.id).order_by(Address.created_at))).scalars().all()
    return [{"id": str(a.id), "label": a.label, "full_name": a.full_name, "phone": a.phone, "address_line1": a.address_line1, "city": a.city, "state": a.state, "postal_code": a.postal_code, "country": a.country, "is_default": a.is_default} for a in items]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_address(body: AddressRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if body.is_default:
        await db.execute(update(Address).where(Address.user_id == user.id).values(is_default=False))
    addr = Address(user_id=user.id, **body.model_dump())
    db.add(addr)
    await db.flush()
    return {"id": str(addr.id), "message": "Address created"}


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(address_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    addr = (await db.execute(select(Address).where(Address.id == address_id, Address.user_id == user.id))).scalar_one_or_none()
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    was_default = addr.is_default
    await db.delete(addr)
    if was_default:
        next_addr = (await db.execute(select(Address).where(Address.user_id == user.id).limit(1))).scalar_one_or_none()
        if next_addr:
            next_addr.is_default = True
    await db.flush()
