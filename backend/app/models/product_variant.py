from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    attributes_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    compare_at_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3), nullable=True)
    image_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("product_images.id", ondelete="SET NULL"), nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="variants")
    image = relationship("ProductImage")
