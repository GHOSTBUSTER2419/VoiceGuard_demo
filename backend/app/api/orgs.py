"""
VoiceGuard — Organization Config API Routes

GET  /api/v1/orgs/{id}/config — Get org risk configuration
PUT  /api/v1/orgs/{id}/config — Update org risk configuration
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.services.session_manager import get_org_config, update_org_config

router = APIRouter(prefix="/api/v1/orgs", tags=["Organizations"])


class OrgConfigResponse(BaseModel):
    org_id: str
    risk_threshold: int
    workflow: str
    transaction_thresholds: Optional[dict] = None


class UpdateOrgConfigRequest(BaseModel):
    risk_threshold: Optional[int] = Field(None, ge=0, le=100)
    workflow: Optional[str] = None


@router.get("/{org_id}/config")
async def api_get_org_config(
    org_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get organization risk policy configuration."""
    config = await get_org_config(db, org_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Organization '{org_id}' not found")

    return {
        "org_id": config.org_id,
        "risk_threshold": config.risk_threshold,
        "workflow": config.workflow,
        "transaction_thresholds": config.transaction_thresholds,
    }


@router.put("/{org_id}/config")
async def api_update_org_config(
    org_id: str,
    req: UpdateOrgConfigRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update organization risk configuration.

    The backend enforces these thresholds — the frontend only displays them.
    """
    try:
        config = await update_org_config(
            db=db,
            org_id=org_id,
            risk_threshold=req.risk_threshold,
            workflow=req.workflow,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "org_id": config.org_id,
        "risk_threshold": config.risk_threshold,
        "workflow": config.workflow,
        "status": "updated",
    }
