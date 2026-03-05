from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.design_settings import DesignSettings
from app.schemas.design import DesignUpdate


class DesignService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_design(self, carousel_id: UUID) -> DesignSettings | None:
        result = await self._db.execute(
            select(DesignSettings).where(DesignSettings.carousel_id == carousel_id)
        )
        return result.scalar_one_or_none()

    async def update_design(self, carousel_id: UUID, payload: DesignUpdate) -> DesignSettings | None:
        design = await self.get_design(carousel_id)
        if not design:
            return None
        data = payload.model_dump(exclude_unset=True)
        if "apply_to_all" in data:
            del data["apply_to_all"]
        for key, value in data.items():
            setattr(design, key, value)
        await self._db.flush()
        return design
