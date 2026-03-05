from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SlideRead(BaseModel):
    id: UUID
    carousel_id: UUID
    order: int
    title: str
    body: str
    footer: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SlideUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    footer: Optional[str] = None
