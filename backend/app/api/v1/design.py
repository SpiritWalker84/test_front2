from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_carousel_service, get_design_service
from app.schemas.design import DesignRead, DesignUpdate
from app.services.carousel_service import CarouselService
from app.services.design_service import DesignService

router = APIRouter()


@router.get("/{id}/design", response_model=DesignRead)
async def get_design(
    id: UUID,
    carousel_svc: CarouselService = Depends(get_carousel_service),
    design_svc: DesignService = Depends(get_design_service),
):
    carousel = await carousel_svc.get_carousel(id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    design = await design_svc.get_design(id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design


@router.patch("/{id}/design", response_model=DesignRead)
async def update_design(
    id: UUID,
    payload: DesignUpdate,
    carousel_svc: CarouselService = Depends(get_carousel_service),
    design_svc: DesignService = Depends(get_design_service),
):
    carousel = await carousel_svc.get_carousel(id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    design = await design_svc.update_design(id, payload)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design
