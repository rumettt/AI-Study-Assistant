from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import Config
from fastapi import UploadFile

from app.core.config import settings


ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class StorageService:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            use_ssl=settings.s3_use_ssl,
            config=Config(signature_version="s3v4"),
        )

    def ensure_bucket(self) -> None:
        buckets = self.client.list_buckets().get("Buckets", [])
        if any(bucket["Name"] == settings.s3_bucket_name for bucket in buckets):
            return
        self.client.create_bucket(Bucket=settings.s3_bucket_name)

    def build_key(self, user_id: str, filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        return f"users/{user_id}/documents/{uuid4()}{suffix}"

    def upload_file(self, file: UploadFile, storage_key: str) -> None:
        self.ensure_bucket()
        file.file.seek(0)
        self.client.upload_fileobj(
            file.file,
            settings.s3_bucket_name,
            storage_key,
            ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
        )

    def download_file(self, storage_key: str, destination_path: str) -> None:
        self.client.download_file(settings.s3_bucket_name, storage_key, destination_path)
