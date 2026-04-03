from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_admin_user
from ..models import ApprovalStatus, User, utcnow
from ..schemas import ApprovalRequest
from ..services.accounts import add_audit_log, build_status_payload, latest_subscription_for_user


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    payload = []

    for user in users:
        subscription = latest_subscription_for_user(db, user.id)
        status_payload = build_status_payload(user, subscription)
        payload.append(
            {
                "id": user.id,
                "email": user.email,
                "fullName": user.full_name,
                "approvalStatus": user.approval_status.value,
                "role": user.role.value,
                "isEmailVerified": user.is_email_verified,
                "createdAt": user.created_at.isoformat() if user.created_at else None,
                "state": status_payload["state"],
                "subscriptionStatus": status_payload["subscription"]["status"],
            }
        )

    return {"users": payload}


@router.post("/approve-user")
def approve_user(
    payload: ApprovalRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    if payload.decision not in {"approved", "rejected"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid approval payload.")

    target_user = db.query(User).filter(User.id == payload.target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found.")

    if payload.decision == "approved" and not target_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Users must verify their email before they can be approved.",
        )

    if payload.decision == "approved":
        target_user.approval_status = ApprovalStatus.APPROVED
        target_user.approved_at = utcnow()
        target_user.approved_by = admin_user.id
        target_user.rejected_reason = None
    else:
        target_user.approval_status = ApprovalStatus.REJECTED
        target_user.approved_at = None
        target_user.approved_by = None
        target_user.rejected_reason = (payload.rejected_reason or "").strip() or "Rejected by admin"

    add_audit_log(
        db,
        actor_user_id=admin_user.id,
        target_user_id=target_user.id,
        action=f"user_{payload.decision}",
        details={"rejectedReason": target_user.rejected_reason} if payload.decision == "rejected" else {},
    )
    db.commit()

    return {"ok": True}

