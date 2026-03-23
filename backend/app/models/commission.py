from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Commission(Base):
    __tablename__ = "commissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    order_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    commission_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    seller_payout: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    payout_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("payouts.id", ondelete="SET NULL"), nullable=True)
    calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    order_item = relationship("OrderItem")
    seller = relationship("Seller")
    payout = relationship("Payout")
