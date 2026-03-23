from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.user import User
from app.models.seller import Seller
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, SellerApplicationRequest, ChangePasswordRequest
from app.schemas.user import UserResponse
from app.schemas.common import MessageResponse
from app.utils.hashing import hash_password, verify_password
from app.utils.tokens import create_access_token, create_refresh_token, decode_refresh_token, generate_verification_token
from app.utils.slug_utils import generate_unique_slug

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=body.email.lower(), first_name=body.first_name, last_name=body.last_name,
        password_hash=hash_password(body.password), role="buyer",
        email_verification_token=generate_verification_token(),
    )
    db.add(user)
    await db.flush()
    return TokenResponse(access_token=create_access_token(user.id, user.role), refresh_token=create_refresh_token(user.id))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active or user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    return TokenResponse(access_token=create_access_token(user.id, user.role), refresh_token=create_refresh_token(user.id))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_refresh_token(body.refresh_token)
        user_id = uuid.UUID(payload["sub"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from e
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return TokenResponse(access_token=create_access_token(user.id, user.role), refresh_token=create_refresh_token(user.id))


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user.id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(u)


@router.post("/apply-seller", response_model=MessageResponse)
async def apply_as_seller(body: SellerApplicationRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Check not already a seller
    existing = await db.execute(select(Seller).where(Seller.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already applied as seller")

    seller = Seller(
        user_id=user.id, store_name=body.store_name, store_slug=generate_unique_slug(body.store_name),
        store_description=body.store_description, business_name=body.business_name,
        business_type=body.business_type, tax_id=body.tax_id,
        commission_rate=settings.default_commission_rate,
    )
    db.add(seller)

    # Update user role
    result = await db.execute(select(User).where(User.id == user.id))
    u = result.scalar_one()
    u.role = "seller"
    await db.flush()

    return MessageResponse(message="Seller application submitted")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(body: ChangePasswordRequest, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user.id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not verify_password(body.current_password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password incorrect")
    u.password_hash = hash_password(body.new_password)
    await db.flush()
    return MessageResponse(message="Password changed")
