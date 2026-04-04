from __future__ import annotations

import smtplib
from email.message import EmailMessage

from ..config import get_settings


def send_verification_email(email: str, full_name: str | None, token: str, app_base_url: str | None = None) -> dict:
    settings = get_settings()
    public_base_url = (app_base_url or settings.app_base_url).rstrip("/")
    verification_url = f"{public_base_url}/verify-email?token={token}"

    if not settings.smtp_host or not settings.smtp_from_email:
        return {
            "emailDelivery": "preview",
            "verificationUrl": verification_url,
        }

    message = EmailMessage()
    message["Subject"] = "Verify your NexAlpha account"
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = email
    message.set_content(
        "\n".join(
            [
                f"Hi {full_name or 'there'},",
                "",
                "Welcome to NexAlpha.",
                "Verify your email address by opening the link below:",
                verification_url,
                "",
                "After verification, your account will wait for admin approval before billing and product access unlock.",
            ]
        )
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        return {
            "emailDelivery": "preview",
            "verificationUrl": verification_url,
        }

    return {
        "emailDelivery": "smtp",
        "verificationUrl": None,
    }
