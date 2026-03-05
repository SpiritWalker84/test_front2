from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carousel import Carousel, CarouselStatus
from app.models.design_settings import DesignSettings
from app.models.slide import Slide
from app.schemas.carousel import CarouselCreate, CarouselFormat, CarouselUpdate


class CarouselService:
    """Business logic for carousels and slides."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def list_carousels(
        self,
        status: str | None = None,
        lang: str | None = None,
    ) -> list[Carousel]:
        q = select(Carousel).order_by(Carousel.created_at.desc())
        if status:
            q = q.where(Carousel.status == status)
        if lang:
            q = q.where(Carousel.language == lang)
        result = await self._db.execute(q)
        return list(result.scalars().all())

    async def get_carousel(self, carousel_id: UUID, include_slides: bool = False) -> Carousel | None:
        q = select(Carousel).where(Carousel.id == carousel_id)
        result = await self._db.execute(q)
        carousel = result.scalar_one_or_none()
        if carousel and include_slides:
            await self._db.refresh(carousel, ["slides", "design_settings"])
        return carousel

    async def create_carousel(self, payload: CarouselCreate) -> Carousel:
        fmt = payload.get_format()
        carousel = Carousel(
            title=payload.title,
            source_type=payload.source_type,
            source_payload=payload.source_payload or {},
            style_hint=fmt.style_hint,
            language=fmt.language,
            slides_count=fmt.slides_count,
            status=CarouselStatus.draft.value,
        )
        self._db.add(carousel)
        await self._db.flush()

        design = DesignSettings(
            carousel_id=carousel.id,
            template="classic",
            bg_type="color",
            bg_color="#ffffff",
            padding=32,
            align_horizontal="center",
            align_vertical="center",
        )
        self._db.add(design)

        for i in range(1, carousel.slides_count + 1):
            slide = Slide(carousel_id=carousel.id, order=i, title="", body="")
            self._db.add(slide)

        await self._db.flush()
        return carousel

    async def duplicate_carousel(self, source_id: UUID) -> Carousel | None:
        """Создать новую карусель как копию существующей (текст + дизайн, без генераций/экспортов)."""
        source = await self.get_carousel(source_id, include_slides=True)
        if not source:
            return None

        carousel = Carousel(
            title=source.title,
            status=CarouselStatus.draft.value,
            language=source.language,
            slides_count=source.slides_count,
            source_type=source.source_type,
            source_payload=source.source_payload or {},
            style_hint=source.style_hint,
        )
        self._db.add(carousel)
        await self._db.flush()

        # Копируем дизайн, если он есть
        if source.design_settings:
            src_d = source.design_settings
            design = DesignSettings(
                carousel_id=carousel.id,
                template=src_d.template,
                bg_type=src_d.bg_type,
                bg_color=src_d.bg_color,
                bg_image_url=src_d.bg_image_url,
                bg_dim_amount=src_d.bg_dim_amount,
                padding=src_d.padding,
                align_horizontal=src_d.align_horizontal,
                align_vertical=src_d.align_vertical,
                show_header=src_d.show_header,
                header_text=src_d.header_text,
                show_footer=src_d.show_footer,
                footer_text=src_d.footer_text,
            )
            self._db.add(design)

        # Копируем слайды
        for s in source.slides:
            slide = Slide(
                carousel_id=carousel.id,
                order=s.order,
                title=s.title,
                body=s.body,
                footer=s.footer,
            )
            self._db.add(slide)

        await self._db.flush()
        return carousel

    async def update_carousel(self, carousel_id: UUID, payload: CarouselUpdate) -> Carousel | None:
        carousel = await self.get_carousel(carousel_id)
        if not carousel:
            return None
        if payload.title is not None:
            carousel.title = payload.title
        if payload.format is not None:
            carousel.language = payload.format.language
            carousel.slides_count = payload.format.slides_count
            carousel.style_hint = payload.format.style_hint
        await self._db.flush()
        return carousel

    async def delete_carousel(self, carousel_id: UUID) -> bool:
        carousel = await self.get_carousel(carousel_id)
        if not carousel:
            return False
        await self._db.delete(carousel)
        await self._db.flush()
        return True

    async def get_first_slides_map(
        self, carousel_ids: list[UUID]
    ) -> dict[UUID, tuple[str, str]]:
        """Для каждого carousel_id возвращает (title, body) первого слайда (order=1)."""
        if not carousel_ids:
            return {}
        result = await self._db.execute(
            select(Slide.carousel_id, Slide.title, Slide.body).where(
                Slide.carousel_id.in_(carousel_ids),
                Slide.order == 1,
            )
        )
        return {row.carousel_id: (row.title or "", (row.body or "")[:120]) for row in result.all()}

    async def get_slides(self, carousel_id: UUID) -> list[Slide]:
        result = await self._db.execute(
            select(Slide).where(Slide.carousel_id == carousel_id).order_by(Slide.order)
        )
        return list(result.scalars().all())

    async def get_slide(self, carousel_id: UUID, slide_id: UUID) -> Slide | None:
        result = await self._db.execute(
            select(Slide).where(Slide.id == slide_id, Slide.carousel_id == carousel_id)
        )
        return result.scalar_one_or_none()

    async def update_slide(
        self,
        carousel_id: UUID,
        slide_id: UUID,
        title: str | None = None,
        body: str | None = None,
        footer: str | None = None,
    ) -> Slide | None:
        slide = await self.get_slide(carousel_id, slide_id)
        if not slide:
            return None
        if title is not None:
            slide.title = title
        if body is not None:
            slide.body = body
        if footer is not None:
            slide.footer = footer
        await self._db.flush()
        return slide
