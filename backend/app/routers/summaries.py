from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.dependencies import get_current_user
from app.models.summary import Summary
from app.models.user import User
from app.schemas.ai import SummaryResponse
from app.services.summarisation_service import SummarisationService


router = APIRouter()


@router.get("/{document_id}", response_model=SummaryResponse)
def get_summary(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> SummaryResponse:
    summary = db.query(Summary).filter(Summary.document_id == document_id).one_or_none()
    if summary is None or summary.document.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
    return summary


@router.post("/{document_id}", response_model=SummaryResponse)
@limiter.limit(settings.ai_request_limit)
def generate_summary(
    request: Request,
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
) -> SummaryResponse:
    del request
    try:
        return SummarisationService().generate(db, document_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
