from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.dependencies import get_current_user
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.ai import QuizAttemptRequest, QuizAttemptResponse, QuizResponse
from app.services.quiz_service import QuizService


router = APIRouter()


@router.post("/{document_id}", response_model=QuizResponse)
@limiter.limit(settings.ai_request_limit)
def generate_quiz(
    request: Request,
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> QuizResponse:
    del request
    try:
        return QuizService().generate(db, document_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> QuizResponse:
    quiz = db.get(Quiz, quiz_id)
    if quiz is None or quiz.document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/attempts", response_model=QuizAttemptResponse)
def submit_quiz_attempt(
    quiz_id: str,
    payload: QuizAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> QuizAttemptResponse:
    try:
        attempt = QuizService().score(db, quiz_id, current_user.id, payload.answers)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return QuizAttemptResponse(score=attempt.score, total=attempt.total)
