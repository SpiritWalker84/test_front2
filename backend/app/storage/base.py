from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorage(ABC):
    @abstractmethod
    async def upload(
        self,
        key: str,
        body: BinaryIO,
        content_type: str,
    ) -> str:
        """Upload file, return public URL."""
        ...

    @abstractmethod
    async def ensure_bucket(self) -> None:
        """Create bucket if not exists."""
        ...
