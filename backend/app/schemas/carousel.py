from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CarouselFormat(BaseModel):
    slides_count: int = Field(ge=6, le=10, default=8)
    language: str = Field(pattern="^(ru|en|fr)$", default="ru")
    style_hint: Optional[str] = None


class CarouselCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512, default="Untitled")
    source_type: str = Field(pattern="^(text|video|links)$", default="text")
    source_payload: Optional[dict[str, Any]] = None
    format: Optional[CarouselFormat] = None

    def get_format(self) -> CarouselFormat:
        return self.format or CarouselFormat()


class CarouselUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=512)
    format: Optional[CarouselFormat] = None


class CarouselRead(BaseModel):
    id: UUID
    title: str
    status: str
    language: str
    slides_count: int
    source_type: str
    preview_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CarouselListRead(CarouselRead):
    """Для списка: опционально первый слайд (заголовок + обрезок текста)."""
    first_slide_title: Optional[str] = None
    first_slide_body: Optional[str] = None
