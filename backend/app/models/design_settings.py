import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.carousel import Carousel


class DesignSettings(Base, TimestampMixin):
    __tablename__ = "design_settings"

    id: Mapped[uuid.UUID] = uuid_pk()
    carousel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carousels.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    template: Mapped[str] = mapped_column(String(32), nullable=False, default="classic")
    bg_type: Mapped[str] = mapped_column(String(16), nullable=False, default="color")
    bg_color: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    bg_image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    bg_dim_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    padding: Mapped[int] = mapped_column(Integer, nullable=False, default=32)
    align_horizontal: Mapped[str] = mapped_column(String(16), nullable=False, default="center")
    align_vertical: Mapped[str] = mapped_column(String(16), nullable=False, default="center")

    # Текстовый стиль
    title_font_size: Mapped[int] = mapped_column(Integer, nullable=False, default=32)
    body_font_size: Mapped[int] = mapped_column(Integer, nullable=False, default=18)
    highlight_color: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    show_header: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    header_text: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    show_footer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    footer_text: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    carousel: Mapped["Carousel"] = relationship("Carousel", back_populates="design_settings")
