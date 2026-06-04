from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.session import Session
from app.models.user import User


def register_user(db: DbSession, email: str, password: str) -> User:
    existing = db.scalar(select(User).where(User.email == email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(email=email.lower(), password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: DbSession, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return user


def issue_tokens(db: DbSession, user: User) -> tuple[str, str]:
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    payload = decode_token(refresh_token, expected_type="refresh")
    if payload is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not issue token")

    session = Session(
        user_id=user.id,
        refresh_token_id=str(payload["jti"]),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(session)
    db.commit()
    return access_token, refresh_token


def refresh_tokens(db: DbSession, refresh_token: str) -> tuple[User, str, str]:
    payload = decode_token(refresh_token, expected_type="refresh")
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = str(payload["sub"])
    token_id = str(payload["jti"])
    session = db.scalar(
        select(Session).where(
            Session.user_id == user_id,
            Session.refresh_token_id == token_id,
            Session.expires_at > datetime.now(UTC),
        )
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session expired")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")

    db.delete(session)
    db.commit()
    access_token, new_refresh_token = issue_tokens(db, user)
    return user, access_token, new_refresh_token
