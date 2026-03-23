from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # percentage/fixed_amount/free_shipping
    value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    min_order_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    max_discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    applicable_to: Mapped[str] = mapped_column(String(30), nullable=False, default="all")
    applicable_ids_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    per_user_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User")
