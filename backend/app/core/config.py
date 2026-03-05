from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = Field(default=True, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    database_url: str = Field(..., alias="DATABASE_URL")

    s3_endpoint_url: str = Field(default="http://minio:9000", alias="S3_ENDPOINT_URL")
    s3_access_key: str = Field(default="minioadmin", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minioadmin", alias="S3_SECRET_KEY")
    s3_bucket_name: str = Field(default="carousel-assets", alias="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_use_ssl: bool = Field(default=False, alias="S3_USE_SSL")

    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")
    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")

    export_viewport_width: int = Field(default=1080, alias="EXPORT_VIEWPORT_WIDTH")
    export_viewport_height: int = Field(default=1350, alias="EXPORT_VIEWPORT_HEIGHT")
    playwright_browser_path: str = Field(
        default="/usr/bin/chromium", alias="PLAYWRIGHT_BROWSER_PATH"
    )

    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
