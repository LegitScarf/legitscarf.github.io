from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ApprovalRequest(BaseModel):
    target_user_id: str = Field(min_length=1)
    decision: str
    rejected_reason: str | None = None


class PromoteAdminRequest(BaseModel):
    email: EmailStr
