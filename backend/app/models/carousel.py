import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.design_settings import DesignSettings
    from app.models.export import Export
    from app.models.generation import Generation
    from app.models.slide import Slide


class CarouselStatus(str, Enum):
    draft = "draft"
    generating = "generating"
    ready = "ready"
    failed = "failed"


class SourceType(str, Enum):
    text = "text"
    video = "video"
    links = "links"


class Carousel(Base, TimestampMixin):
    __tablename__ = "carousels"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="Untitled")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=CarouselStatus.draft.value
    )
    language: Mapped[str] = mapped_column(String(8), nullable=False, default="ru")
    slides_count: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    source_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=SourceType.text.value
    )
    source_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    style_hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preview_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    design_settings: Mapped[Optional["DesignSettings"]] = relationship(
        "DesignSettings",
        back_populates="carousel",
        uselist=False,
        cascade="all, delete-orphan",
    )
    slides: Mapped[list["Slide"]] = relationship(
        "Slide",
        back_populates="carousel",
        order_by="Slide.order",
        cascade="all, delete-orphan",
    )
    generations: Mapped[list["Generation"]] = relationship(
        "Generation",
        back_populates="carousel",
        order_by="Generation.created_at",
        cascade="all, delete-orphan",
    )
    exports: Mapped[list["Export"]] = relationship(
        "Export",
        back_populates="carousel",
        cascade="all, delete-orphan",
    )
