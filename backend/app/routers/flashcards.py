from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.dependencies import get_current_user
from app.models.flashcard import FlashcardSet
from app.models.user import User
from app.schemas.ai import FlashcardSetResponse
from app.services.flashcard_service import FlashcardService


router = APIRouter()


@router.post("/{document_id}", response_model=FlashcardSetResponse)
@limiter.limit(settings.ai_request_limit)
def generate_flashcards(
    request: Request,
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> FlashcardSetResponse:
    del request
    try:
        return FlashcardService().generate(db, document_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/{set_id}", response_model=FlashcardSetResponse)
def get_flashcard_set(
    set_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> FlashcardSetResponse:
    flashcard_set = db.get(FlashcardSet, set_id)
    if flashcard_set is None or flashcard_set.document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard set not found")
    return flashcard_set


@router.get("/{set_id}/export")
def export_flashcards(
    set_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> Response:
    try:
        content = FlashcardService().export_apkg(db, set_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="study-flashcards.apkg"'},
    )
