from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SubscriptionStatus(str, enum.Enum):
    PENDING = "pending"
    CREATED = "created"
    AUTHENTICATED = "authenticated"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    HALTED = "halted"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class AppRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    approval_status = Column(SqlEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    role = Column(SqlEnum(AppRole), nullable=False, default=AppRole.USER)
    is_email_verified = Column(Boolean, nullable=False, default=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    rejected_reason = Column(Text, nullable=True)
    email_verification_token_hash = Column(String(64), nullable=True, index=True)
    email_verification_sent_at = Column(DateTime(timezone=True), nullable=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    gateway = Column(String(32), nullable=False, default="razorpay")
    gateway_customer_id = Column(String(255), nullable=True)
    gateway_subscription_id = Column(String(255), nullable=True, unique=True, index=True)
    gateway_plan_id = Column(String(255), nullable=True)
    status = Column(SqlEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.PENDING)
    amount_inr = Column(Integer, nullable=False, default=500)
    currency = Column(String(12), nullable=False, default="INR")
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False, default=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"), nullable=True)
    gateway = Column(String(32), nullable=False, default="razorpay")
    gateway_payment_id = Column(String(255), nullable=True, unique=True, index=True)
    gateway_invoice_id = Column(String(255), nullable=True)
    amount = Column(Integer, nullable=False, default=0)
    currency = Column(String(12), nullable=False, default="INR")
    status = Column(String(64), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    raw_payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    target_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

