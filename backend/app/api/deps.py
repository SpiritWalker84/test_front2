from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.carousel_service import CarouselService
from app.services.design_service import DesignService
from app.services.generation_service import GenerationService
from app.services.export_service import ExportService
from app.services.storage_service import StorageService
from app.storage.s3 import S3Storage


def get_carousel_service(db: AsyncSession = Depends(get_db)) -> CarouselService:
    return CarouselService(db)


def get_design_service(db: AsyncSession = Depends(get_db)) -> DesignService:
    return DesignService(db)


def get_generation_service(db: AsyncSession = Depends(get_db)) -> GenerationService:
    return GenerationService(db)


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    return ExportService(db)


def get_storage_service(db: AsyncSession = Depends(get_db)) -> StorageService:
    return StorageService(db, S3Storage())


async def get_carousel_id(
    id: UUID,
    svc: CarouselService,
) -> UUID:
    carousel = await svc.get_carousel(id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    return id
