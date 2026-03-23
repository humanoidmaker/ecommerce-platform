from typing import Optional
import uuid
from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    values_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # list of strings
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="attributes")
