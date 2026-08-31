"""
VoiceGuard — Demo Simulation API Routes

POST /api/v1/demo/simulate — Trigger genuine or cloned simulation
POST /api/v1/demo/stop     — Stop running simulation
GET  /api/v1/demo/status   — Get demo system status
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.config import settings
from app.models.mock_model import MockModelProvider

router = APIRouter(prefix="/api/v1/demo", tags=["Demo"])


class SimulateRequest(BaseModel):
    type: str  # "genuine" or "cloned"
    org_id: str = "default"
    transaction_type: str = "FUND_TRANSFER"
    transaction_value: float = 250000.0
    speaker_label: str = "CFO - Rajesh Kumar"
    language: str = "en"


@router.post("/simulate")
async def trigger_simulation(
    req: SimulateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a demo simulation.

    The simulation creates a real session and streams results through the
    WebSocket pipeline. It is NOT a frontend-only animation.

    Types:
    - "genuine": Scores stay low (NORMAL state)
    - "cloned": Scores escalate to CRITICAL, triggering step-up
    """
    if req.type not in ("genuine", "cloned"):
        raise HTTPException(
            status_code=400,
            detail="Simulation type must be 'genuine' or 'cloned'",
        )

    # Session creation and WebSocket streaming are handled by the WS endpoint.
    # This endpoint returns the parameters needed to initiate the simulation.
    from app.services.session_manager import create_session

    session = await create_session(
        db=db,
        org_id=req.org_id,
        speaker_label=req.speaker_label,
        language=req.language,
        transaction_type=req.transaction_type,
        transaction_value=req.transaction_value,
        is_demo=True,
    )

    return {
        "session_id": session.id,
        "sim_type": req.type,
        "status": "ready",
        "message": f"Session created. Connect to WebSocket /api/v1/sessions/{session.id}/stream to start simulation.",
        "transaction_type": req.transaction_type,
        "transaction_value": req.transaction_value,
        "speaker_label": req.speaker_label,
    }


@router.get("/status")
async def demo_status():
    """Get demo system status including model mode."""
    model = MockModelProvider()
    return {
        "mode": settings.model_mode,
        "model_status": model.get_status(),
        "system": "online",
        "demo_available": True,
    }
