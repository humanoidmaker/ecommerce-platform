from typing import Optional
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # ["wireless", "bluetooth"]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    compare_at_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False, default=Decimal("0.0800"))
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 3), nullable=True)
    dimensions_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_digital: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    digital_file_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    has_variants: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)  # draft/active/inactive/out_of_stock/archived
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="public")
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_bestseller: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    condition: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=Decimal("0.00"))
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wishlist_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    meta_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    seller = relationship("Seller", back_populates="products")
    category = relationship("Category")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan", order_by="ProductVariant.sort_order")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
