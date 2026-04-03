from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..dependencies import get_current_user_optional
from ..models import ApprovalStatus, AppRole, User, utcnow
from ..schemas import LoginRequest, RegisterRequest
from ..security import (
    clear_session_cookie,
    create_session_token,
    generate_verification_token,
    hash_password,
    hash_token,
    set_session_cookie,
    verify_password,
)
from ..services.accounts import add_audit_log, serialize_user
from ..services.email import send_verification_email


router = APIRouter(prefix="/api/auth", tags=["auth"])
verification_router = APIRouter(tags=["auth"])


def _utc(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=utcnow().tzinfo)
    return value


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    existing = db.query(User).filter(User.email == email).first()
    raw_token, token_hash_value = generate_verification_token()
    now = utcnow()
    settings = get_settings()

    if existing and existing.is_email_verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    if existing:
        user = existing
        user.full_name = payload.full_name.strip()
        user.password_hash = hash_password(payload.password)
        user.approval_status = ApprovalStatus.PENDING
        user.approved_at = None
        user.approved_by = None
        user.rejected_reason = None
        user.is_email_verified = False
        user.email_verification_token_hash = token_hash_value
        user.email_verification_sent_at = now
        user.email_verification_expires_at = now + timedelta(hours=settings.verification_token_ttl_hours)
        add_audit_log(db, action="verification_resent", target_user_id=user.id, details={"email": email})
    else:
        user = User(
            email=email,
            full_name=payload.full_name.strip(),
            password_hash=hash_password(payload.password),
            approval_status=ApprovalStatus.PENDING,
            role=AppRole.USER,
            is_email_verified=False,
            email_verification_token_hash=token_hash_value,
            email_verification_sent_at=now,
            email_verification_expires_at=now + timedelta(hours=settings.verification_token_ttl_hours),
        )
        db.add(user)
        db.flush()
        add_audit_log(db, action="user_registered", target_user_id=user.id, details={"email": email})

    db.commit()

    delivery = send_verification_email(user.email, user.full_name, raw_token)
    return {
        "ok": True,
        "verificationRequired": True,
        "emailDelivery": delivery["emailDelivery"],
        "verificationUrl": delivery["verificationUrl"],
    }


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_session_token(user.id, user.role.value)
    set_session_cookie(response, token)
    return {
        "ok": True,
        "user": serialize_user(user),
    }


@router.post("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"ok": True}


@router.get("/session")
def session(user: User | None = Depends(get_current_user_optional)):
    if not user:
        return {"authenticated": False, "user": None}

    return {
        "authenticated": True,
        "user": serialize_user(user),
    }


@verification_router.get("/verify-email")
def verify_email(token: str = Query(min_length=1), db: Session = Depends(get_db)):
    settings = get_settings()
    token_hash_value = hash_token(token)
    user = db.query(User).filter(User.email_verification_token_hash == token_hash_value).first()

    if not user:
        return RedirectResponse(
            url=f"{settings.app_base_url}/login.html?verification=invalid",
            status_code=status.HTTP_302_FOUND,
        )

    expires_at = _utc(user.email_verification_expires_at)
    if expires_at and expires_at < utcnow():
        return RedirectResponse(
            url=f"{settings.app_base_url}/login.html?verification=expired",
            status_code=status.HTTP_302_FOUND,
        )

    user.is_email_verified = True
    user.email_verification_token_hash = None
    user.email_verification_sent_at = None
    user.email_verification_expires_at = None
    add_audit_log(db, action="email_verified", target_user_id=user.id)
    db.commit()

    return RedirectResponse(url=f"{settings.app_base_url}/login.html?verified=1", status_code=status.HTTP_302_FOUND)
