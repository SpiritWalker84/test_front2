from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carousel import Carousel
from app.models.export import Export
from app.models.slide import Slide


class ExportService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_export(self, export_id: UUID) -> Export | None:
        result = await self._db.execute(select(Export).where(Export.id == export_id))
        return result.scalar_one_or_none()

    async def create_export(self, carousel_id: UUID) -> Export | None:
        carousel = await self._db.get(Carousel, carousel_id)
        if not carousel:
            return None
        exp = Export(carousel_id=carousel_id, status="queued")
        self._db.add(exp)
        await self._db.flush()
        return exp

    async def set_export_done(self, export_id: UUID, zip_url: str) -> None:
        exp = await self.get_export(export_id)
        if exp:
            exp.status = "done"
            exp.zip_url = zip_url
            await self._db.flush()

    async def set_export_failed(self, export_id: UUID, error_message: str) -> None:
        exp = await self.get_export(export_id)
        if exp:
            exp.status = "failed"
            exp.error_message = error_message[:2000]
            await self._db.flush()

    async def get_carousel_with_slides_and_design(self, carousel_id: UUID) -> Carousel | None:
        carousel = await self._db.get(Carousel, carousel_id)
        if not carousel:
            return None
        await self._db.refresh(carousel, ["slides", "design_settings"])
        return carousel
