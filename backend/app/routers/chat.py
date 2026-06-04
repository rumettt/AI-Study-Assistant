from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.ai import ChatRequest, ChatResponse
from app.services.chat_service import ChatService


router = APIRouter()


@router.post("", response_model=ChatResponse)
@limiter.limit(settings.ai_request_limit)
def chat(
    request: Request,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> ChatResponse:
    del request
    try:
        conversation_id, answer, citations = ChatService().answer(
            db, current_user.id, payload.question, payload.conversation_id
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return ChatResponse(conversation_id=conversation_id, answer=answer, citations=citations)
