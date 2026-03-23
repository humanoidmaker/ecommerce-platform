from typing import Optional
import uuid
import datetime as dt
from decimal import Decimal
from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AggregateStats(Base):
    __tablename__ = "aggregate_stats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stat_date: Mapped[dt.date] = mapped_column(Date, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    units_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_order_value: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    new_customers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    returning_customers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conversion_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=Decimal("0.0000"))
    top_products_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    top_categories_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
