"""
VoiceGuard — Session Manager

Manages call session lifecycle: creation, retrieval, and updates.
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CallSession, OrgConfig, Alert, SessionFeature
from app.privacy.audio_policy import mask_phone_number


async def create_session(
    db: AsyncSession,
    org_id: str = "default",
    origin: Optional[str] = None,
    speaker_label: Optional[str] = None,
    language: str = "en",
    accent_profile: Optional[str] = None,
    transaction_type: Optional[str] = None,
    transaction_value: Optional[float] = None,
    known_contact: bool = False,
    is_demo: bool = False,
) -> CallSession:
    """
    Create a new call session.

    PRIVACY: Call origin is masked before storage.
    """
    session = CallSession(
        id=str(uuid.uuid4()),
        org_id=org_id,
        origin=mask_phone_number(origin) if origin else None,
        speaker_label=speaker_label,
        language=language,
        accent_profile=accent_profile,
        transaction_type=transaction_type,
        transaction_value=transaction_value,
        known_contact=known_contact,
        is_demo=is_demo,
    )
    db.add(session)
    await db.flush()
    return session


async def get_session(db: AsyncSession, session_id: str) -> Optional[CallSession]:
    """Retrieve a session by ID."""
    result = await db.execute(
        select(CallSession).where(CallSession.id == session_id)
    )
    return result.scalar_one_or_none()


async def end_session(
    db: AsyncSession,
    session_id: str,
    final_risk_score: float,
    verdict: str,
    step_up_triggered: bool = False,
    step_up_method: Optional[str] = None,
    step_up_completed: bool = False,
) -> Optional[CallSession]:
    """End a session with final risk assessment."""
    session = await get_session(db, session_id)
    if session:
        session.ended_at = datetime.utcnow()
        session.final_risk_score = final_risk_score
        session.verdict = verdict
        session.step_up_triggered = step_up_triggered
        session.step_up_method = step_up_method
        session.step_up_completed = step_up_completed
        await db.flush()
    return session


async def save_feature(
    db: AsyncSession,
    session_id: str,
    window_index: int,
    spectral_score: float,
    prosody_score: float,
    speaker_match_score: float,
    fused_score: float,
    risk_state: str,
    latency_ms: float = 0.0,
    reasons: Optional[list] = None,
) -> SessionFeature:
    """
    Save per-window feature scores.

    PRIVACY: Only numerical scores are stored. Raw audio is never persisted.
    """
    feature = SessionFeature(
        id=str(uuid.uuid4()),
        session_id=session_id,
        window_index=window_index,
        spectral_score=spectral_score,
        prosody_score=prosody_score,
        speaker_match_score=speaker_match_score,
        fused_score=fused_score,
        risk_state=risk_state,
        latency_ms=latency_ms,
        reasons=reasons,
    )
    db.add(feature)
    await db.flush()
    return feature


async def get_org_config(db: AsyncSession, org_id: str = "default") -> Optional[OrgConfig]:
    """Get organization configuration."""
    result = await db.execute(
        select(OrgConfig).where(OrgConfig.org_id == org_id)
    )
    return result.scalar_one_or_none()


async def update_org_config(
    db: AsyncSession,
    org_id: str,
    risk_threshold: Optional[int] = None,
    workflow: Optional[str] = None,
) -> Optional[OrgConfig]:
    """Update organization risk configuration."""
    config = await get_org_config(db, org_id)
    if config is None:
        config = OrgConfig(org_id=org_id)
        db.add(config)

    if risk_threshold is not None:
        config.risk_threshold = risk_threshold
    if workflow is not None:
        if workflow not in ("otp", "callback", "supervisor"):
            raise ValueError(f"Invalid workflow: {workflow}. Must be otp, callback, or supervisor.")
        config.workflow = workflow

    config.updated_at = datetime.utcnow()
    await db.flush()
    return config


async def create_alert(
    db: AsyncSession,
    session_id: str,
    org_id: str,
    risk_score: float,
    risk_state: str,
    transaction_type: Optional[str] = None,
    transaction_value: Optional[float] = None,
) -> Alert:
    """Create a security alert."""
    alert = Alert(
        id=str(uuid.uuid4()),
        session_id=session_id,
        org_id=org_id,
        risk_score=risk_score,
        risk_state=risk_state,
        transaction_type=transaction_type,
        transaction_value=transaction_value,
    )
    db.add(alert)
    await db.flush()
    return alert
