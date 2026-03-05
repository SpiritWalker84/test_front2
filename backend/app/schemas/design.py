from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DesignUpdate(BaseModel):
    template: Optional[str] = Field(None, pattern="^(classic|bold|minimal)$")
    bg_type: Optional[str] = Field(None, pattern="^(color|image)$")
    bg_color: Optional[str] = None
    bg_image_url: Optional[str] = None
    bg_dim_amount: Optional[float] = Field(None, ge=0, le=1)
    padding: Optional[int] = Field(None, ge=0, le=200)
    align_horizontal: Optional[str] = Field(None, pattern="^(left|center|right)$")
    align_vertical: Optional[str] = Field(None, pattern="^(top|center|bottom)$")
    show_header: Optional[bool] = None
    header_text: Optional[str] = None
    show_footer: Optional[bool] = None
    footer_text: Optional[str] = None
    title_font_size: Optional[int] = Field(None, ge=10, le=72)
    body_font_size: Optional[int] = Field(None, ge=8, le=48)
    highlight_color: Optional[str] = None
    apply_to_all: Optional[bool] = None  # MVP: ignored, one design for all


class DesignRead(BaseModel):
    id: UUID
    carousel_id: UUID
    template: str
    bg_type: str
    bg_color: Optional[str] = None
    bg_image_url: Optional[str] = None
    bg_dim_amount: float
    padding: int
    align_horizontal: str
    align_vertical: str
    title_font_size: int
    body_font_size: int
    highlight_color: Optional[str] = None
    show_header: bool
    header_text: Optional[str] = None
    show_footer: bool
    footer_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
