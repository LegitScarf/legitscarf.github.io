from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user_optional
from ..models import User
from ..services.accounts import build_status_payload, latest_subscription_for_user


router = APIRouter(prefix="/api/account", tags=["account"])


@router.get("/status")
def status_endpoint(
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not user:
        return {
            "state": "guest",
            "canAccessApps": False,
            "subscription": {
                "status": None,
                "currentPeriodEnd": None,
            },
        }

    subscription = latest_subscription_for_user(db, user.id)
    return build_status_payload(user, subscription)

