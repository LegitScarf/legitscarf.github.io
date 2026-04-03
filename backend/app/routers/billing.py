from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import ApprovalStatus, Subscription, SubscriptionStatus, User
from ..services.accounts import add_audit_log, build_status_payload, latest_subscription_for_user
from ..services.razorpay import create_remote_subscription, normalize_subscription_status, unix_to_datetime


router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.post("/create-subscription")
def create_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subscription = latest_subscription_for_user(db, current_user.id)
    status_payload = build_status_payload(current_user, subscription)

    if current_user.approval_status != ApprovalStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account must be approved before you can subscribe.",
        )

    if status_payload["subscription"]["status"] == SubscriptionStatus.ACTIVE.value and status_payload["canAccessApps"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This account already has an active subscription.",
        )

    try:
        remote = create_remote_subscription(user_id=current_user.id)
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error)) from error

    record = None
    if remote.get("id"):
        record = db.query(Subscription).filter(Subscription.gateway_subscription_id == remote["id"]).first()

    if not record:
        record = Subscription(
            user_id=current_user.id,
            gateway="razorpay",
        )
        db.add(record)

    record.gateway_customer_id = remote.get("customer_id")
    record.gateway_subscription_id = remote.get("id")
    record.gateway_plan_id = remote.get("plan_id")
    record.status = normalize_subscription_status(remote.get("status"))
    record.amount_inr = 500
    record.currency = "INR"
    record.current_period_start = unix_to_datetime(remote.get("current_start"))
    record.current_period_end = unix_to_datetime(remote.get("current_end"))
    record.metadata_json = {
        "notes": {
            "source": "nexalpha",
            "user_id": current_user.id,
        }
    }

    add_audit_log(
        db,
        actor_user_id=current_user.id,
        target_user_id=current_user.id,
        action="subscription_created",
        details={"gateway_subscription_id": record.gateway_subscription_id},
    )
    db.commit()

    return {
        "checkoutUrl": remote.get("short_url"),
        "subscriptionId": remote.get("id"),
        "status": remote.get("status"),
    }
