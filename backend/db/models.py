"""
VoxShield — Database Models
SQLAlchemy ORM models for SQLite.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer,
    JSON, String, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    calls = relationship("Call", back_populates="user", cascade="all, delete-orphan")
    trusted_contacts = relationship("TrustedContact", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Call(Base):
    __tablename__ = "calls"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    caller_number = Column(String(30), nullable=True)
    caller_name = Column(String(255), nullable=True)   # If matched to contact
    timestamp = Column(DateTime, default=func.now(), index=True)
    duration_seconds = Column(Integer, nullable=True)
    language = Column(String(10), nullable=True)        # ISO 639-1
    action_taken = Column(String(20), nullable=True)    # BLOCKED | CONTINUED | VERIFIED | ENDED
    is_demo = Column(Boolean, default=False)            # True = seeded demo data
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="calls")
    analysis = relationship("CallAnalysis", back_populates="call", uselist=False, cascade="all, delete-orphan")


class CallAnalysis(Base):
    __tablename__ = "call_analysis"

    id = Column(String(36), primary_key=True, default=_uuid)
    call_id = Column(String(36), ForeignKey("calls.id"), unique=True, nullable=False)

    # ASR outputs
    transcript = Column(Text, nullable=True)
    asr_model = Column(String(100), nullable=True)
    asr_latency_ms = Column(Float, nullable=True)

    # Deepfake detection
    voice_fake_probability = Column(Float, nullable=True)   # 0.0–1.0, None if unavailable
    voice_real_probability = Column(Float, nullable=True)
    voice_label = Column(String(50), nullable=True)         # real | spoof | uncertain | unavailable
    deepfake_model = Column(String(100), nullable=True)
    deepfake_latency_ms = Column(Float, nullable=True)

    # Scam analysis
    scam_probability = Column(Float, nullable=True)
    scam_category = Column(String(50), nullable=True)
    scam_severity = Column(String(20), nullable=True)
    scam_signals = Column(JSON, nullable=True)              # list of signal strings
    financial_request = Column(Boolean, default=False)
    urgency_detected = Column(Boolean, default=False)
    identity_claim = Column(Boolean, default=False)

    # Risk engine
    risk_score = Column(Integer, nullable=True)             # 0–100
    risk_level = Column(String(20), nullable=True)          # LOW | CAUTION | HIGH | CRITICAL
    risk_reasons = Column(JSON, nullable=True)              # list of reason strings
    risk_actions = Column(JSON, nullable=True)              # list of action strings
    risk_components = Column(JSON, nullable=True)           # component breakdown

    # Timing
    total_latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())

    call = relationship("Call", back_populates="analysis")


class CallerProfile(Base):
    __tablename__ = "caller_profiles"

    id = Column(String(36), primary_key=True, default=_uuid)
    phone_number = Column(String(30), unique=True, nullable=False, index=True)
    first_seen = Column(DateTime, default=func.now())
    last_seen = Column(DateTime, default=func.now())
    total_calls = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)               # Times risk >= HIGH
    average_risk_score = Column(Float, default=0.0)
    most_common_category = Column(String(50), nullable=True)
    is_blocked = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())


class TrustedContact(Base):
    __tablename__ = "trusted_contacts"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    contact_relationship = Column(String(50), nullable=True)   # father | mother | friend | bank | etc.
    phone_number = Column(String(30), nullable=False)
    is_enrolled = Column(Boolean, default=False)               # Voice enrolled for speaker verification
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="trusted_contacts")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    audio_retention_enabled = Column(Boolean, default=False)
    transcript_retention_days = Column(Integer, default=30)
    alert_on_high_risk = Column(Boolean, default=True)
    alert_on_caution = Column(Boolean, default=False)
    preferred_language = Column(String(10), default="en")
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="settings")
