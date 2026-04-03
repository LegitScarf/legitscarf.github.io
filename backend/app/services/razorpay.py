from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import datetime, timezone

import httpx

from ..config import get_settings
from ..models import SubscriptionStatus


def unix_to_datetime(value: int | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc)


def normalize_subscription_status(value: str | None) -> SubscriptionStatus:
    fallback = SubscriptionStatus.PENDING
    if not value:
        return fallback

    try:
        return SubscriptionStatus(value)
    except ValueError:
        return fallback


def create_remote_subscription(*, user_id: str) -> dict:
    settings = get_settings()

    if not settings.razorpay_key_id or not settings.razorpay_key_secret or not settings.razorpay_plan_id:
        raise RuntimeError(
            "Razorpay is not configured yet. Add RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, and RAZORPAY_PLAN_ID."
        )

    payload = {
        "plan_id": settings.razorpay_plan_id,
        "total_count": 1200,
        "quantity": 1,
        "customer_notify": True,
        "notes": {
            "source": "nexalpha",
            "user_id": user_id,
        },
    }

    auth = base64.b64encode(
        f"{settings.razorpay_key_id}:{settings.razorpay_key_secret}".encode("utf-8")
    ).decode("utf-8")

    response = httpx.post(
        "https://api.razorpay.com/v1/subscriptions",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )

    data = response.json()
    if response.status_code >= 400:
        description = data.get("error", {}).get("description") if isinstance(data, dict) else None
        raise RuntimeError(description or "Unable to create Razorpay subscription.")

    return data


def verify_webhook_signature(body: bytes, signature: str | None) -> bool:
    settings = get_settings()
    if not signature or not settings.razorpay_webhook_secret:
        return False

    expected = hmac.new(
        settings.razorpay_webhook_secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
