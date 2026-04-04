from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import ApprovalStatus, AppRole, AuditLog, Subscription, SubscriptionStatus, User


def latest_subscription_for_user(db: Session, user_id: str) -> Subscription | None:
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id)
        .order_by(Subscription.created_at.desc())
        .first()
    )


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "fullName": user.full_name,
        "role": user.role.value if isinstance(user.role, AppRole) else str(user.role),
    }


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if not value:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _is_active_subscription(subscription: Subscription | None) -> bool:
    if not subscription or subscription.status != SubscriptionStatus.ACTIVE:
        return False

    current_end = _normalize_datetime(subscription.current_period_end)
    if not current_end:
        return True

    return current_end > datetime.now(timezone.utc)


def _is_admin(user: User) -> bool:
    return user.role == AppRole.ADMIN


def compute_account_state(user: User, subscription: Subscription | None) -> str:
    if _is_admin(user):
        return "active"

    if not user.is_email_verified:
        return "registered_unverified"

    if user.approval_status == ApprovalStatus.PENDING:
        return "verified_pending_approval"

    if user.approval_status == ApprovalStatus.REJECTED:
        return "suspended"

    if user.approval_status == ApprovalStatus.APPROVED and not subscription:
        return "approved_unsubscribed"

    if subscription and subscription.status in {
        SubscriptionStatus.PENDING,
        SubscriptionStatus.CREATED,
        SubscriptionStatus.AUTHENTICATED,
    }:
        return "approved_subscription_pending"

    if _is_active_subscription(subscription):
        return "active"

    if subscription and subscription.status in {
        SubscriptionStatus.CANCELLED,
        SubscriptionStatus.COMPLETED,
        SubscriptionStatus.EXPIRED,
        SubscriptionStatus.HALTED,
        SubscriptionStatus.PAST_DUE,
    }:
        return "suspended"

    if user.approval_status == ApprovalStatus.APPROVED:
        return "approved_unsubscribed"

    return "guest"


def build_status_payload(user: User, subscription: Subscription | None = None) -> dict:
    active = _is_admin(user) or _is_active_subscription(subscription)
    current_end = _normalize_datetime(subscription.current_period_end) if subscription else None
    return {
        "state": compute_account_state(user, subscription),
        "approvalStatus": user.approval_status.value,
        "role": user.role.value,
        "isAdmin": _is_admin(user),
        "canAccessApps": _is_admin(user) or (
            user.approval_status == ApprovalStatus.APPROVED and user.is_email_verified and active
        ),
        "email": user.email,
        "fullName": user.full_name,
        "subscription": {
            "status": subscription.status.value if subscription else None,
            "currentPeriodEnd": current_end.isoformat() if current_end else None,
        },
    }


def add_audit_log(
    db: Session,
    *,
    action: str,
    actor_user_id: str | None = None,
    target_user_id: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            action=action,
            details=details or {},
        )
    )
