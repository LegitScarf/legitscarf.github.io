from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import PROJECT_ROOT, get_settings
from .database import SessionLocal, init_database
from .models import AppRole, ApprovalStatus, User
from .routers.account import router as account_router
from .routers.admin import router as admin_router
from .routers.auth import router as auth_router, verification_router
from .routers.billing import router as billing_router
from .routers.dev import router as dev_router
from .routers.webhooks import router as webhooks_router
from .security import hash_password


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins) or [settings.app_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(verification_router)
app.include_router(account_router)
app.include_router(billing_router)
app.include_router(admin_router)
app.include_router(dev_router)
app.include_router(webhooks_router)

assets_dir = PROJECT_ROOT / "assets"
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


def serve_page(filename: str) -> FileResponse:
    return FileResponse(PROJECT_ROOT / filename)


@app.on_event("startup")
def startup() -> None:
    init_database()
    bootstrap_admin_user()


def bootstrap_admin_user() -> None:
    if not settings.bootstrap_admin_email or not settings.bootstrap_admin_password:
        return

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.bootstrap_admin_email.lower().strip()).first()
        if not admin:
            admin = User(
                email=settings.bootstrap_admin_email.lower().strip(),
                full_name=settings.bootstrap_admin_name,
                password_hash=hash_password(settings.bootstrap_admin_password),
                role=AppRole.ADMIN,
                approval_status=ApprovalStatus.APPROVED,
                is_email_verified=True,
            )
            db.add(admin)
        else:
            admin.full_name = admin.full_name or settings.bootstrap_admin_name
            admin.password_hash = hash_password(settings.bootstrap_admin_password)
            admin.role = AppRole.ADMIN
            admin.approval_status = ApprovalStatus.APPROVED
            admin.is_email_verified = True
        db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/")
def index():
    return serve_page("index.html")


@app.get("/index.html")
def index_html():
    return serve_page("index.html")


@app.get("/login.html")
def login_html():
    return serve_page("login.html")


@app.get("/register.html")
def register_html():
    return serve_page("register.html")


@app.get("/account.html")
def account_html():
    return serve_page("account.html")


@app.get("/access.html")
def access_html():
    return serve_page("access.html")


@app.get("/admin.html")
def admin_html():
    return serve_page("admin.html")
