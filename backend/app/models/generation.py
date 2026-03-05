import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.carousel import Carousel


class Generation(Base, TimestampMixin):
    __tablename__ = "generations"

    id: Mapped[uuid.UUID] = uuid_pk()
    carousel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carousels.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    request_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    result_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    carousel: Mapped["Carousel"] = relationship("Carousel", back_populates="generations")
