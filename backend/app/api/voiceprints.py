"""
VoiceGuard — Voiceprint API Routes

POST /api/v1/voiceprints — Enroll a consent-based voiceprint

PRIVACY: Only embeddings are stored, never raw audio recordings.
Enrollment requires explicit consent (consent_given=True).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db.models import Voiceprint
from app.privacy.audio_policy import AudioPolicy

import uuid

router = APIRouter(prefix="/api/v1/voiceprints", tags=["Voiceprints"])


class EnrollVoiceprintRequest(BaseModel):
    org_id: str
    person_label: str
    # Embedding vector (list of floats) — NOT raw audio
    embedding: list[float]
    consent_given: bool


@router.post("")
async def enroll_voiceprint(
    req: EnrollVoiceprintRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Enroll a voiceprint for speaker verification.

    PRIVACY:
    - Requires explicit consent (consent_given must be True)
    - Only stores the embedding vector, never raw audio
    - The embedding is a mathematical representation, not a recording
    """
    # Enforce consent requirement
    AudioPolicy.validate_consent(req.consent_given, context="voiceprint enrollment")

    voiceprint = Voiceprint(
        id=str(uuid.uuid4()),
        org_id=req.org_id,
        person_label=req.person_label,
        embedding=req.embedding,
        consent_given=req.consent_given,
        consent_ts=datetime.utcnow() if req.consent_given else None,
    )
    db.add(voiceprint)

    return {
        "id": voiceprint.id,
        "person_label": voiceprint.person_label,
        "status": "enrolled",
        "consent_recorded": True,
    }
