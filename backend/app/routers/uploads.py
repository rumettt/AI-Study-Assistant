from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.storage_service import ALLOWED_CONTENT_TYPES, ALLOWED_EXTENSIONS, StorageService
from app.tasks.document_tasks import process_document


router = APIRouter()


@router.post("", response_model=DocumentResponse, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> Document:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a PDF, PPTX, or DOCX file",
        )

    size = 0
    chunk_size = 1024 * 1024
    while chunk := file.file.read(chunk_size):
        size += len(chunk)
        if size > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds {settings.max_upload_size_mb}MB limit",
            )

    storage = StorageService()
    storage_key = storage.build_key(current_user.id, filename)
    storage.upload_file(file, storage_key)

    document = Document(
        user_id=current_user.id,
        original_filename=filename,
        content_type=file.content_type or "application/octet-stream",
        storage_key=storage_key,
        size_bytes=size,
        status="queued",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    process_document.delay(document.id)
    return document
