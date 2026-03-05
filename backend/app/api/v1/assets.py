from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_storage_service
from app.schemas.asset import AssetRead
from app.services.storage_service import StorageService

router = APIRouter()


@router.post("/upload", response_model=AssetRead, status_code=201)
async def upload_asset(
    file: UploadFile = File(...),
    carousel_id: UUID | None = None,
    svc: StorageService = Depends(get_storage_service),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    content_type = file.content_type or "application/octet-stream"
    filename = file.filename or "upload"
    asset = await svc.upload_asset(content, filename, content_type, carousel_id)
    return asset
