from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentStatusResponse


router = APIRouter()


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> DocumentStatusResponse:
    document = db.get(Document, document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunk_count = db.scalar(select(func.count()).select_from(Chunk).where(Chunk.document_id == document.id)) or 0
    return DocumentStatusResponse(
        id=document.id,
        status=document.status,
        error_message=document.error_message,
        chunk_count=chunk_count,
        processed_at=document.processed_at,
    )
