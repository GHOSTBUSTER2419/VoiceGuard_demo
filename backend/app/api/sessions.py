"""
VoiceGuard — Session API Routes

POST /api/v1/sessions       — Create a new call session
GET  /api/v1/sessions/{id}  — Get session details with score history
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.engine import get_db
from app.db.models import CallSession, SessionFeature
from app.services.session_manager import create_session, get_session

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])


class CreateSessionRequest(BaseModel):
    org_id: str = "default"
    origin: Optional[str] = None
    speaker_label: Optional[str] = None
    language: str = "en"
    accent_profile: Optional[str] = None
    transaction_type: Optional[str] = None
    transaction_value: Optional[float] = None
    known_contact: bool = False
    is_demo: bool = False


class SessionResponse(BaseModel):
    id: str
    org_id: str
    origin: Optional[str] = None
    speaker_label: Optional[str] = None
    language: str = "en"
    transaction_type: Optional[str] = None
    transaction_value: Optional[float] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    final_risk_score: Optional[float] = None
    step_up_triggered: bool = False
    verdict: Optional[str] = None
    is_demo: bool = False
    score_history: list[dict] = Field(default_factory=list)


@router.post("", response_model=dict)
async def api_create_session(
    req: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new call session for monitoring."""
    session = await create_session(
        db=db,
        org_id=req.org_id,
        origin=req.origin,
        speaker_label=req.speaker_label,
        language=req.language,
        accent_profile=req.accent_profile,
        transaction_type=req.transaction_type,
        transaction_value=req.transaction_value,
        known_contact=req.known_contact,
        is_demo=req.is_demo,
    )
    return {"session_id": session.id, "status": "created"}


@router.get("/{session_id}")
async def api_get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get session details including score history."""
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get score history
    result = await db.execute(
        select(SessionFeature)
        .where(SessionFeature.session_id == session_id)
        .order_by(SessionFeature.window_index)
    )
    features = result.scalars().all()

    score_history = [
        {
            "window_index": f.window_index,
            "ts": f.window_ts.isoformat() if f.window_ts else None,
            "spectral_score": f.spectral_score,
            "prosody_score": f.prosody_score,
            "speaker_match_score": f.speaker_match_score,
            "fused_score": f.fused_score,
            "risk_state": f.risk_state,
        }
        for f in features
    ]

    return {
        "id": session.id,
        "org_id": session.org_id,
        "origin": session.origin,
        "speaker_label": session.speaker_label,
        "language": session.language,
        "transaction_type": session.transaction_type,
        "transaction_value": session.transaction_value,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "final_risk_score": session.final_risk_score,
        "step_up_triggered": session.step_up_triggered,
        "verdict": session.verdict,
        "is_demo": session.is_demo,
        "score_history": score_history,
    }
