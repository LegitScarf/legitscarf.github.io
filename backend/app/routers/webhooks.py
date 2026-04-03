from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request, status

from ..database import SessionLocal
from ..models import Payment, Subscription
from ..services.accounts import add_audit_log
from ..services.razorpay import normalize_subscription_status, unix_to_datetime, verify_webhook_signature


router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature")

    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature.")

    payload = json.loads(body.decode("utf-8"))
    event = payload.get("event", "unknown")
    subscription_data = payload.get("payload", {}).get("subscription", {}).get("entity", {})
    payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})

    gateway_subscription_id = subscription_data.get("id")
    if not gateway_subscription_id:
        return {"ok": True}

    db = SessionLocal()
    payment_id = payment_data.get("id")
    try:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.gateway_subscription_id == gateway_subscription_id)
            .first()
        )
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription record not found for webhook event.",
            )

        subscription.status = normalize_subscription_status(subscription_data.get("status"))
        subscription.gateway_customer_id = subscription_data.get("customer_id")
        subscription.current_period_start = unix_to_datetime(subscription_data.get("current_start"))
        subscription.current_period_end = unix_to_datetime(subscription_data.get("current_end"))
        subscription.cancel_at_period_end = bool(subscription_data.get("cancel_at_cycle_end", False))
        subscription.metadata_json = payload

        if payment_id:
            payment = db.query(Payment).filter(Payment.gateway_payment_id == payment_id).first()
            if not payment:
                payment = Payment(
                    user_id=subscription.user_id,
                    subscription_id=subscription.id,
                    gateway="razorpay",
                    gateway_payment_id=payment_id,
                    status=payment_data.get("status") or event,
                )
                db.add(payment)

            payment.gateway_invoice_id = payment_data.get("invoice_id")
            payment.amount = payment_data.get("amount", 0)
            payment.currency = payment_data.get("currency", "INR")
            payment.status = payment_data.get("status") or event
            payment.paid_at = unix_to_datetime(payment_data.get("created_at"))
            payment.raw_payload = payload

        add_audit_log(
            db,
            action=f"razorpay_{event}",
            target_user_id=subscription.user_id,
            details={
                "subscription_id": gateway_subscription_id,
                "payment_id": payment_id,
            },
        )
        db.commit()
    finally:
        db.close()

    return {"ok": True}

