"""
VoiceGuard — Database Models

SQLAlchemy ORM models for all persistent data.

PRIVACY POLICY:
    Raw audio is NEVER stored in any table.
    Only embeddings, scores, timestamps, and metadata are persisted.
    Voiceprints are embeddings — not recordings.
    Call origin is stored in masked/hashed form.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Voiceprint(Base):
    """
    Enrolled voiceprint for speaker verification.

    PRIVACY: Stores only the embedding vector, never raw audio.
    Enrollment requires explicit consent.
    """
    __tablename__ = "voiceprints"

    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, nullable=False, index=True)
    person_label = Column(String, nullable=False)
    # Embedding stored as JSON array of floats
    # In production with pgvector, this would use the Vector type
    embedding = Column(JSON, nullable=False)
    consent_given = Column(Boolean, nullable=False, default=False)
    consent_ts = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CallSession(Base):
    """
    A single monitored voice call session.

    PRIVACY: No raw audio is stored. Only scores and metadata.
    Call origin is masked (e.g., +91 ******4821).
    """
    __tablename__ = "call_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, nullable=False, index=True)
    # Masked caller origin — never store full phone numbers in cleartext
    origin = Column(String, nullable=True)
    speaker_label = Column(String, nullable=True)
    language = Column(String, default="en")
    accent_profile = Column(String, nullable=True)
    transaction_type = Column(String, nullable=True)
    transaction_value = Column(Float, nullable=True)
    known_contact = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    final_risk_score = Column(Float, nullable=True)
    step_up_triggered = Column(Boolean, default=False)
    step_up_method = Column(String, nullable=True)
    step_up_completed = Column(Boolean, default=False)
    # verdict: genuine | flagged | blocked | verified
    verdict = Column(String, nullable=True)
    is_demo = Column(Boolean, default=False)

    # Relationships
    features = relationship("SessionFeature", back_populates="session", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="session", cascade="all, delete-orphan")


class SessionFeature(Base):
    """
    Per-window feature scores for a call session.

    PRIVACY: Contains only numerical scores extracted from audio windows.
    Raw audio is processed in memory and immediately discarded.
    """
    __tablename__ = "session_features"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("call_sessions.id"), nullable=False, index=True)
    window_index = Column(Integer, nullable=False)
    window_ts = Column(DateTime, default=datetime.utcnow)
    spectral_score = Column(Float, nullable=False)
    prosody_score = Column(Float, nullable=False)
    speaker_match_score = Column(Float, nullable=False)
    fused_score = Column(Float, nullable=False)
    risk_state = Column(String, nullable=False)
    latency_ms = Column(Float, nullable=True)
    reasons = Column(JSON, nullable=True)

    session = relationship("CallSession", back_populates="features")


class OrgConfig(Base):
    """
    Per-organization risk policy configuration.

    Thresholds and workflows are configurable per org.
    The backend enforces these — the frontend only displays them.
    """
    __tablename__ = "org_config"

    org_id = Column(String, primary_key=True)
    risk_threshold = Column(Integer, nullable=False, default=70)
    # workflow: otp | callback | supervisor
    workflow = Column(String, nullable=False, default="otp")
    # Context-aware thresholds per transaction type (JSON dict)
    transaction_thresholds = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """
    Security alert raised when risk exceeds threshold.

    Supports analyst feedback for future model improvement loop.
    """
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("call_sessions.id"), nullable=False, index=True)
    org_id = Column(String, nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_state = Column(String, nullable=False)
    transaction_type = Column(String, nullable=True)
    transaction_value = Column(Float, nullable=True)
    raised_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    # analyst_feedback: true_positive | false_positive | null
    analyst_feedback = Column(String, nullable=True)
    feedback_ts = Column(DateTime, nullable=True)
    feedback_notes = Column(Text, nullable=True)

    session = relationship("CallSession", back_populates="alerts")
