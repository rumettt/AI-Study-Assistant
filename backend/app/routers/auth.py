from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import authenticate_user, issue_tokens, refresh_tokens, register_user


router = APIRouter()


def token_response(user, access_token: str, refresh_token: str) -> TokenResponse:
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(id=user.id, email=user.email),
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: DbSession = Depends(get_db)) -> TokenResponse:
    user = register_user(db, payload.email, payload.password)
    access_token, refresh_token = issue_tokens(db, user)
    return token_response(user, access_token, refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    access_token, refresh_token = issue_tokens(db, user)
    return token_response(user, access_token, refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: DbSession = Depends(get_db)) -> TokenResponse:
    user, access_token, refresh_token = refresh_tokens(db, payload.refresh_token)
    return token_response(user, access_token, refresh_token)
