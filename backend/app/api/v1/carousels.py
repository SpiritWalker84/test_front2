from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_carousel_service
from app.schemas.carousel import CarouselCreate, CarouselListRead, CarouselRead, CarouselUpdate
from app.services.carousel_service import CarouselService

router = APIRouter()


@router.get("", response_model=list[CarouselListRead])
async def list_carousels(
    status: str | None = Query(None),
    lang: str | None = Query(None, alias="lang"),
    include_first_slide: bool = Query(False),
    svc: CarouselService = Depends(get_carousel_service),
):
    items = await svc.list_carousels(status=status, lang=lang)
    if not include_first_slide:
        return [CarouselListRead.model_validate(c) for c in items]
    ids = [c.id for c in items]
    first_map = await svc.get_first_slides_map(ids)
    out = []
    for c in items:
        data = CarouselListRead.model_validate(c)
        if c.id in first_map:
            title, body = first_map[c.id]
            data.first_slide_title = title
            data.first_slide_body = body
        out.append(data)
    return out


@router.get("/{id}", response_model=CarouselRead)
async def get_carousel(
    id: UUID,
    include_slides: bool = Query(False),
    svc: CarouselService = Depends(get_carousel_service),
):
    carousel = await svc.get_carousel(id, include_slides=include_slides)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    return carousel


@router.post("", response_model=CarouselRead, status_code=201)
async def create_carousel(
    payload: CarouselCreate,
    svc: CarouselService = Depends(get_carousel_service),
):
    carousel = await svc.create_carousel(payload)
    return carousel


@router.post("/{id}/duplicate", response_model=CarouselRead, status_code=201)
async def duplicate_carousel(
    id: UUID,
    svc: CarouselService = Depends(get_carousel_service),
):
    carousel = await svc.duplicate_carousel(id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    return carousel


@router.patch("/{id}", response_model=CarouselRead)
async def update_carousel(
    id: UUID,
    payload: CarouselUpdate,
    svc: CarouselService = Depends(get_carousel_service),
):
    carousel = await svc.update_carousel(id, payload)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    return carousel


@router.delete("/{id}", status_code=204)
async def delete_carousel(
    id: UUID,
    svc: CarouselService = Depends(get_carousel_service),
):
    ok = await svc.delete_carousel(id)
    if not ok:
        raise HTTPException(status_code=404, detail="Carousel not found")
