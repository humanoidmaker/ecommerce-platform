from typing import Optional
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    order_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="SET NULL"), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    images_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    seller_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seller_responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product")
    buyer = relationship("User")
