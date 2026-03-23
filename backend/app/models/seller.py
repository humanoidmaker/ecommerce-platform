from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Seller(Base):
    __tablename__ = "sellers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    store_name: Mapped[str] = mapped_column(String(200), nullable=False)
    store_slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    store_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    banner_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    business_name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    business_type: Mapped[str] = mapped_column(String(20), nullable=False, default="individual")  # individual/company
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_account_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=Decimal("0.1500"))
    payout_schedule: Mapped[str] = mapped_column(String(20), nullable=False, default="biweekly")
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_products: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=Decimal("0.00"))
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    application_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending/approved/rejected/suspended
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    return_policy_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shipping_policy_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="seller")
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
