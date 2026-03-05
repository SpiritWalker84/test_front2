from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.api.deps import get_carousel_service, get_export_service
from app.schemas.export import ExportCreate, ExportRead
from app.services.carousel_service import CarouselService
from app.services.export_service import ExportService
from app.tasks.export import run_export_task

router = APIRouter()


@router.post("", response_model=ExportRead, status_code=202)
async def create_export(
    payload: ExportCreate,
    background_tasks: BackgroundTasks,
    carousel_svc: CarouselService = Depends(get_carousel_service),
    export_svc: ExportService = Depends(get_export_service),
):
    carousel_id = payload.carousel_id
    carousel = await carousel_svc.get_carousel(carousel_id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    exp = await export_svc.create_export(carousel_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Carousel not found")
    background_tasks.add_task(run_export_task, exp.id)
    return exp


@router.get("/{id}", response_model=ExportRead)
async def get_export(
    id: UUID,
    export_svc: ExportService = Depends(get_export_service),
):
    exp = await export_svc.get_export(id)
    if not exp:
        raise HTTPException(status_code=404, detail="Export not found")
    return exp
