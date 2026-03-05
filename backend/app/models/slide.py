import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.carousel import Carousel


class Slide(Base, TimestampMixin):
    __tablename__ = "slides"

    id: Mapped[uuid.UUID] = uuid_pk()
    carousel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carousels.id", ondelete="CASCADE"),
        nullable=False,
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    footer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    carousel: Mapped["Carousel"] = relationship("Carousel", back_populates="slides")
