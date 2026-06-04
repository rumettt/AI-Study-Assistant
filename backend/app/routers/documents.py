from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.flashcard import FlashcardSet
from app.models.quiz import QuizAttempt
from app.models.user import User
from app.schemas.ai import DashboardDocument, DashboardResponse
from app.schemas.document import DocumentResponse, DocumentStatusResponse


router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> list[Document]:
    return list(
        db.scalars(
            select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())
        )
    )


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


@router.get("/dashboard/overview", response_model=DashboardResponse)
def dashboard(
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> DashboardResponse:
    documents = list(
        db.scalars(
            select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc()).limit(20)
        )
    )
    dashboard_documents = [
        DashboardDocument(
            id=document.id,
            original_filename=document.original_filename,
            status=document.status,
            created_at=document.created_at,
            chunk_count=db.scalar(select(func.count()).select_from(Chunk).where(Chunk.document_id == document.id)) or 0,
        )
        for document in documents
    ]
    attempts = list(db.scalars(select(QuizAttempt).where(QuizAttempt.user_id == current_user.id)))
    average = None
    if attempts:
        average = sum(attempt.score / max(attempt.total, 1) for attempt in attempts) / len(attempts)
    flashcard_sets = (
        db.scalar(
            select(func.count())
            .select_from(FlashcardSet)
            .join(Document)
            .where(Document.user_id == current_user.id)
        )
        or 0
    )
    return DashboardResponse(
        documents=dashboard_documents,
        quiz_attempts=len(attempts),
        average_quiz_score=average,
        flashcard_sets=flashcard_sets,
    )
