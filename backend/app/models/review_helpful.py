from typing import Optional
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ReviewHelpful(Base):
    __tablename__ = "review_helpfuls"
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_helpful_review_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    review = relationship("Review")
    user = relationship("User")
