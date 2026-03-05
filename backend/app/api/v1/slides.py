from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_carousel_service
from app.schemas.slide import SlideRead, SlideUpdate
from app.services.carousel_service import CarouselService

router = APIRouter()


@router.get("/{id}/slides", response_model=list[SlideRead])
async def get_slides(
    id: UUID,
    svc: CarouselService = Depends(get_carousel_service),
):
    carousel = await svc.get_carousel(id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    return await svc.get_slides(id)


@router.patch("/{id}/slides/{slide_id}", response_model=SlideRead)
async def update_slide(
    id: UUID,
    slide_id: UUID,
    payload: SlideUpdate,
    svc: CarouselService = Depends(get_carousel_service),
):
    slide = await svc.update_slide(
        id,
        slide_id,
        title=payload.title,
        body=payload.body,
        footer=payload.footer,
    )
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    return slide
