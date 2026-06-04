from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AI Study Assistant API"
    environment: str = "development"
    api_cors_origins: str = "http://localhost:3000"

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    s3_endpoint_url: str | None = None
    s3_region: str = "us-east-1"
    s3_access_key_id: str
    s3_secret_access_key: str
    s3_bucket_name: str = "study-documents"
    s3_use_ssl: bool = False

    max_upload_size_mb: int = Field(default=50, ge=1)

    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"

    pinecone_api_key: str | None = None
    pinecone_index_name: str = "study-helper"
    pinecone_namespace: str = "documents"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_embedding_dimension: int = 1536

    chunk_target_tokens: int = 500
    chunk_overlap_tokens: int = 50

    @field_validator("api_cors_origins")
    @classmethod
    def normalize_origins(cls, value: str) -> str:
        return value.strip()

    @field_validator("openai_api_key", "pinecone_api_key", mode="before")
    @classmethod
    def normalize_optional_secret(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
