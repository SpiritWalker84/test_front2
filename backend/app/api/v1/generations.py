from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_carousel_service, get_generation_service
from app.core.database import get_db
from app.models.carousel import Carousel, CarouselStatus
from app.models.slide import Slide
from app.schemas.generation import GenerationCreate, GenerationRead, LLMGenerationResult
from app.services.carousel_service import CarouselService
from app.services.generation_service import GenerationService
from app.services.openai_client import OpenAIClient

router = APIRouter()

SYSTEM_PROMPT = """You are a copywriter. Given source material, produce a carousel of slides as JSON.
Output ONLY valid JSON in this exact shape, no markdown:
{"slides": [{"order": 1, "title": "...", "body": "...", "footer": "..."}, ...]}
- title: short heading, max 80 chars
- body: main text for the slide, max 400 chars
- footer: optional CTA or note, max 80 chars
Use the requested language. Match the style hint if provided. Number of slides must equal slides_count."""


def _build_user_prompt(carousel: Carousel) -> str:
    payload = carousel.source_payload or {}
    parts = []
    if payload.get("text"):
        parts.append(f"Source text:\n{payload['text']}")
    if payload.get("video_url"):
        parts.append(f"Video URL (use as context only): {payload['video_url']}")
    if payload.get("links"):
        parts.append("Links: " + ", ".join(payload.get("links", [])))
    if payload.get("notes"):
        parts.append(f"Notes: {payload['notes']}")
    parts.append(f"\nLanguage: {carousel.language}. Number of slides: {carousel.slides_count}.")
    if carousel.style_hint:
        parts.append(f"Style hint (match this tone): {carousel.style_hint[:500]}")
    return "\n".join(parts)


@router.post("", response_model=GenerationRead)
async def create_generation(
    payload: GenerationCreate,
    db: AsyncSession = Depends(get_db),
    carousel_svc: CarouselService = Depends(get_carousel_service),
    gen_svc: GenerationService = Depends(get_generation_service),
):
    carousel = await carousel_svc.get_carousel(payload.carousel_id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    gen = await gen_svc.create_generation(payload.carousel_id)
    if not gen:
        raise HTTPException(status_code=404, detail="Carousel not found")

    gen.status = "running"
    await db.flush()

    await db.refresh(carousel)
    user_prompt = _build_user_prompt(carousel)

    try:
        client = OpenAIClient()
        result_payload = await client.generate_json(SYSTEM_PROMPT, user_prompt)
        parsed = LLMGenerationResult.model_validate(result_payload)
        if len(parsed.slides) > carousel.slides_count:
            parsed.slides = parsed.slides[: carousel.slides_count]

        gen.status = "done"
        gen.result_payload = result_payload
        await db.flush()

        result = await db.execute(
            select(Slide).where(Slide.carousel_id == carousel.id).order_by(Slide.order)
        )
        slides = list(result.scalars().all())
        for i, item in enumerate(parsed.slides):
            if i < len(slides):
                slides[i].title = (item.title or "")[:500]
                slides[i].body = (item.body or "")[:3000]
                slides[i].footer = ((item.footer or "")[:500]) or None

        carousel.status = CarouselStatus.ready.value
        await db.flush()
    except Exception as e:
        gen.status = "failed"
        gen.error_message = (str(e))[:2000]
        carousel.status = CarouselStatus.failed.value
        await db.flush()

    await db.refresh(gen)
    return gen


@router.get("/{id}", response_model=GenerationRead)
async def get_generation(
    id: UUID,
    gen_svc: GenerationService = Depends(get_generation_service),
):
    gen = await gen_svc.get_generation(id)
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    return gen
