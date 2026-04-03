from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models import AppRole, ApprovalStatus, User
from ..schemas import PromoteAdminRequest
from ..services.accounts import add_audit_log


router = APIRouter(prefix="/api/dev", tags=["dev"])


@router.post("/promote-admin")
def promote_admin(
    payload: PromoteAdminRequest,
    db: Session = Depends(get_db),
    x_dev_admin_token: str | None = Header(default=None),
):
    settings = get_settings()

    if not settings.enable_dev_tools:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    if not settings.dev_admin_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DEV_ADMIN_TOKEN is not configured.",
        )

    if not x_dev_admin_token or not secrets.compare_digest(x_dev_admin_token, settings.dev_admin_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid dev admin token.")

    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.role = AppRole.ADMIN
    user.approval_status = ApprovalStatus.APPROVED
    user.is_email_verified = True
    user.approved_by = None
    user.rejected_reason = None

    add_audit_log(
        db,
        action="dev_promote_admin",
        target_user_id=user.id,
        details={"email": user.email},
    )
    db.commit()

    return {
        "ok": True,
        "email": user.email,
        "role": user.role.value,
    }
