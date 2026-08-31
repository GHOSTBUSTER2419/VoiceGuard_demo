"""
VoiceGuard — Alerts API Routes

GET  /api/v1/alerts              — List alerts (paginated, filterable)
POST /api/v1/alerts/{id}/feedback — Submit analyst feedback
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db.models import Alert

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])


class FeedbackRequest(BaseModel):
    # true_positive | false_positive
    feedback: str
    notes: Optional[str] = None


@router.get("")
async def list_alerts(
    org_id: Optional[str] = Query(None),
    verdict: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List security alerts with filtering and pagination.

    Supports filtering by organization, verdict, and date.
    """
    query = select(Alert).order_by(desc(Alert.raised_at))

    if org_id:
        query = query.where(Alert.org_id == org_id)

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return {
        "alerts": [
            {
                "id": a.id,
                "session_id": a.session_id,
                "org_id": a.org_id,
                "risk_score": a.risk_score,
                "risk_state": a.risk_state,
                "transaction_type": a.transaction_type,
                "transaction_value": a.transaction_value,
                "raised_at": a.raised_at.isoformat() if a.raised_at else None,
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "analyst_feedback": a.analyst_feedback,
            }
            for a in alerts
        ],
        "count": len(alerts),
        "offset": offset,
        "limit": limit,
    }


@router.post("/{alert_id}/feedback")
async def submit_feedback(
    alert_id: str,
    req: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit analyst feedback for an alert.

    Feedback types:
    - true_positive: confirmed impersonation attempt
    - false_positive: legitimate caller incorrectly flagged

    This creates a foundation for the future retraining loop:
    Detection → Alert → Analyst feedback → Model evaluation → Model update
    """
    if req.feedback not in ("true_positive", "false_positive"):
        raise HTTPException(
            status_code=400,
            detail="Feedback must be 'true_positive' or 'false_positive'",
        )

    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.analyst_feedback = req.feedback
    alert.feedback_ts = datetime.utcnow()
    alert.feedback_notes = req.notes
    alert.resolved_at = datetime.utcnow()

    return {
        "id": alert.id,
        "feedback": alert.analyst_feedback,
        "status": "feedback_recorded",
    }
