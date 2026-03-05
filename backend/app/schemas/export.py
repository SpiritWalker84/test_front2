from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExportCreate(BaseModel):
    carousel_id: UUID


class ExportRead(BaseModel):
    id: UUID
    carousel_id: UUID
    status: str
    zip_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
