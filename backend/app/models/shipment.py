from typing import Optional
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import DateTime, Date, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    carrier: Mapped[str] = mapped_column(String(50), nullable=False, default="internal")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="label_created")
    estimated_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3), nullable=True)
    dimensions_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    label_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tracking_events_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list of {status, location, timestamp, description}
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    order = relationship("Order")
    seller = relationship("Seller")
    warehouse = relationship("Warehouse")
