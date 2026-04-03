from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
DATA_ROOT = BACKEND_ROOT / "data"
DEFAULT_DB_PATH = DATA_ROOT / "nexalpha.db"

load_dotenv(BACKEND_ROOT / ".env")


def _default_database_url() -> str:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"


def _csv_to_tuple(value: str) -> tuple[str, ...]:
    return tuple(item.strip().rstrip("/") for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_base_url: str
    api_base_url: str
    database_url: str
    secret_key: str
    algorithm: str
    session_cookie_name: str
    session_ttl_minutes: int
    session_cookie_secure: bool
    verification_token_ttl_hours: int
    cors_origins: tuple[str, ...]
    razorpay_key_id: str | None
    razorpay_key_secret: str | None
    razorpay_plan_id: str | None
    razorpay_webhook_secret: str | None
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    smtp_use_tls: bool
    smtp_from_email: str | None
    smtp_from_name: str
    bootstrap_admin_email: str | None
    bootstrap_admin_password: str | None
    bootstrap_admin_name: str
    enable_dev_tools: bool
    dev_admin_token: str | None


@lru_cache
def get_settings() -> Settings:
    app_base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    api_base_url = os.getenv("API_BASE_URL", f"{app_base_url}/api").rstrip("/")
    cors_origins = _csv_to_tuple(os.getenv("CORS_ORIGINS", app_base_url))

    return Settings(
        app_name=os.getenv("APP_NAME", "NexAlpha FastAPI"),
        app_base_url=app_base_url,
        api_base_url=api_base_url,
        database_url=os.getenv("DATABASE_URL", _default_database_url()),
        secret_key=os.getenv("SECRET_KEY", "change-me-before-production"),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        session_cookie_name=os.getenv("SESSION_COOKIE_NAME", "nexalpha_session"),
        session_ttl_minutes=int(os.getenv("SESSION_TTL_MINUTES", "10080")),
        session_cookie_secure=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
        verification_token_ttl_hours=int(os.getenv("VERIFICATION_TOKEN_TTL_HOURS", "48")),
        cors_origins=cors_origins,
        razorpay_key_id=os.getenv("RAZORPAY_KEY_ID"),
        razorpay_key_secret=os.getenv("RAZORPAY_KEY_SECRET"),
        razorpay_plan_id=os.getenv("RAZORPAY_PLAN_ID"),
        razorpay_webhook_secret=os.getenv("RAZORPAY_WEBHOOK_SECRET"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        smtp_from_email=os.getenv("SMTP_FROM_EMAIL"),
        smtp_from_name=os.getenv("SMTP_FROM_NAME", "NexAlpha"),
        bootstrap_admin_email=os.getenv("BOOTSTRAP_ADMIN_EMAIL"),
        bootstrap_admin_password=os.getenv("BOOTSTRAP_ADMIN_PASSWORD"),
        bootstrap_admin_name=os.getenv("BOOTSTRAP_ADMIN_NAME", "NexAlpha Admin"),
        enable_dev_tools=os.getenv("ENABLE_DEV_TOOLS", "false").lower() == "true",
        dev_admin_token=os.getenv("DEV_ADMIN_TOKEN"),
    )
