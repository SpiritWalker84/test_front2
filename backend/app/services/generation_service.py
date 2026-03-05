from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carousel import Carousel, CarouselStatus
from app.models.generation import Generation
from app.models.slide import Slide
from app.schemas.generation import LLMGenerationResult


class GenerationService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_generation(self, generation_id: UUID) -> Generation | None:
        result = await self._db.execute(select(Generation).where(Generation.id == generation_id))
        return result.scalar_one_or_none()

    async def create_generation(self, carousel_id: UUID) -> Generation | None:
        carousel = await self._db.get(Carousel, carousel_id)
        if not carousel:
            return None
        gen = Generation(
            carousel_id=carousel_id,
            status="queued",
            request_payload={
                "language": carousel.language,
                "slides_count": carousel.slides_count,
                "source_type": carousel.source_type,
            },
        )
        self._db.add(gen)
        await self._db.flush()
        carousel.status = CarouselStatus.generating.value
        await self._db.flush()
        return gen

    async def set_generation_running(self, generation_id: UUID) -> None:
        gen = await self.get_generation(generation_id)
        if gen:
            gen.status = "running"
            await self._db.flush()

    async def set_generation_done(
        self,
        generation_id: UUID,
        result_payload: dict,
        parsed: LLMGenerationResult,
    ) -> None:
        gen = await self.get_generation(generation_id)
        if not gen:
            return
        gen.status = "done"
        gen.result_payload = result_payload
        await self._db.flush()

        carousel = await self._db.get(Carousel, gen.carousel_id)
        if not carousel:
            return

        result = await self._db.execute(
            select(Slide).where(Slide.carousel_id == carousel.id).order_by(Slide.order)
        )
        slides = list(result.scalars().all())
        for i, item in enumerate(parsed.slides):
            if i < len(slides):
                slides[i].title = item.title[:500] if item.title else ""
                slides[i].body = item.body[:3000] if item.body else ""
                slides[i].footer = (item.footer or "")[:500] or None

        carousel.status = CarouselStatus.ready.value
        await self._db.flush()

    async def set_generation_failed(self, generation_id: UUID, error_message: str) -> None:
        gen = await self.get_generation(generation_id)
        if not gen:
            return
        gen.status = "failed"
        gen.error_message = error_message[:2000]
        await self._db.flush()
        carousel = await self._db.get(Carousel, gen.carousel_id)
        if carousel:
            carousel.status = CarouselStatus.failed.value
            await self._db.flush()
