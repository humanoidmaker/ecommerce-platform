from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="buyer", index=True)  # superadmin, admin, seller, buyer
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verification_token: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    default_shipping_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    default_billing_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    seller = relationship("Seller", back_populates="user", uselist=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
