from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class GenerationCreate(BaseModel):
    carousel_id: UUID


class GenerationRead(BaseModel):
    id: UUID
    carousel_id: UUID
    status: str
    request_payload: Optional[dict[str, Any]] = None
    result_payload: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LLMSlideItem(BaseModel):
    order: int
    title: str
    body: str
    footer: Optional[str] = None


class LLMGenerationResult(BaseModel):
    slides: list[LLMSlideItem]
