from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.carousel import Carousel
from app.schemas.generation import LLMGenerationResult
from app.services.generation_service import GenerationService
from app.services.openai_client import OpenAIClient


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


async def run_generation_task(generation_id: UUID) -> None:
    try:
        carousel_id = None
        async with AsyncSessionLocal() as session:
            gen_svc = GenerationService(session)
            gen = await gen_svc.get_generation(generation_id)
            if not gen:
                return
            carousel_id = gen.carousel_id
            await gen_svc.set_generation_running(generation_id)
            await session.commit()

        async with AsyncSessionLocal() as session:
            carousel = await session.get(Carousel, carousel_id)
            if not carousel:
                return
            await session.refresh(carousel)
            user_prompt = _build_user_prompt(carousel)
            try:
                client = OpenAIClient()
                result_payload = await client.generate_json(SYSTEM_PROMPT, user_prompt)
                parsed = LLMGenerationResult.model_validate(result_payload)
                if len(parsed.slides) > carousel.slides_count:
                    parsed.slides = parsed.slides[: carousel.slides_count]
                gen_svc = GenerationService(session)
                await gen_svc.set_generation_done(generation_id, result_payload, parsed)
                await session.commit()
            except Exception as e:
                gen_svc = GenerationService(session)
                await gen_svc.set_generation_failed(generation_id, str(e))
                await session.commit()
    except Exception as e:
        async with AsyncSessionLocal() as session:
            gen_svc = GenerationService(session)
            await gen_svc.set_generation_failed(generation_id, str(e))
            await session.commit()
        raise
