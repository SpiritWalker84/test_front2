from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.storage.s3 import S3Storage


class StorageService:
    """Upload assets and link to carousel."""

    def __init__(self, db: AsyncSession, storage: S3Storage | None = None):
        self._db = db
        self._storage = storage or S3Storage()

    async def upload_asset(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        carousel_id: UUID | None = None,
    ) -> Asset:
        key = f"assets/{filename}"
        url = self._storage.upload_sync(key, file_content, content_type)
        asset = Asset(type="image", url=url, carousel_id=carousel_id)
        self._db.add(asset)
        await self._db.flush()
        return asset

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        result = await self._db.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()
