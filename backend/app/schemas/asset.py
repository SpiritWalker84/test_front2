from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AssetRead(BaseModel):
    id: UUID
    type: str
    url: str
    carousel_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}
