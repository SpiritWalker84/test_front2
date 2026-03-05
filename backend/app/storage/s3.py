import io
from typing import BinaryIO

from app.core.config import get_settings
from app.storage.base import BaseStorage

settings = get_settings()

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = Exception


class S3Storage(BaseStorage):
    """S3/MinIO storage implementation."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket_name: str | None = None,
        region: str | None = None,
        use_ssl: bool | None = None,
    ):
        s = get_settings()
        self._endpoint_url = endpoint_url or s.s3_endpoint_url
        self._access_key = access_key or s.s3_access_key
        self._secret_key = secret_key or s.s3_secret_key
        self._bucket_name = bucket_name or s.s3_bucket_name
        self._region = region or s.s3_region
        self._use_ssl = use_ssl if use_ssl is not None else s.s3_use_ssl
        self._client = None

    def _get_client(self):
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3Storage. Install with: pip install boto3")
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_key,
                region_name=self._region,
                use_ssl=self._use_ssl,
                config=Config(signature_version="s3v4"),
            )
        return self._client

    async def ensure_bucket(self) -> None:
        client = self._get_client()
        try:
            client.head_bucket(Bucket=self._bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                client.create_bucket(Bucket=self._bucket_name)
            else:
                raise

    async def upload(
        self,
        key: str,
        body: BinaryIO,
        content_type: str,
    ) -> str:
        client = self._get_client()
        await self.ensure_bucket()
        if hasattr(body, "read"):
            data = body.read()
        else:
            data = body
        if isinstance(data, str):
            data = data.encode()
        client.put_object(
            Bucket=self._bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        base = self._endpoint_url.rstrip("/")
        return f"{base}/{self._bucket_name}/{key}"

    def upload_sync(self, key: str, body: BinaryIO | bytes, content_type: str) -> str:
        """Synchronous upload for use in sync background tasks."""
        client = self._get_client()
        if isinstance(body, bytes):
            body = io.BytesIO(body)
        client.put_object(
            Bucket=self._bucket_name,
            Key=key,
            Body=body,
            ContentType=content_type,
        )
        base = self._endpoint_url.rstrip("/")
        return f"{base}/{self._bucket_name}/{key}"
