import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = uuid_pk()
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="image")
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    carousel_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("carousels.id", ondelete="SET NULL"),
        nullable=True,
    )
