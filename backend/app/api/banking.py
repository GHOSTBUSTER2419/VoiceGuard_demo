"""
VoiceGuard — Banking Transaction API Routes

POST /api/v1/banking/check       — Check transaction against risk score
POST /api/v1/banking/step-up     — Request step-up verification
POST /api/v1/banking/verify      — Verify OTP / approval code
POST /api/v1/banking/block       — Block a transaction
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.integrations.banking import MockBankingIntegration
from app.integrations.base import TransactionRequest

import uuid

router = APIRouter(prefix="/api/v1/banking", tags=["Banking"])

# Shared banking integration instance
banking = MockBankingIntegration()


class CheckTransactionRequest(BaseModel):
    transaction_type: str = "FUND_TRANSFER"
    amount: float = 250000.0
    currency: str = "INR"
    beneficiary: str = "ACME SUPPLIERS LTD"
    requested_by: str = "CFO - Rajesh Kumar"
    risk_score: float
    threshold: int = 70
    session_id: Optional[str] = None


class StepUpRequest(BaseModel):
    transaction_id: str
    method: str = "otp"  # otp | callback | supervisor


class VerifyRequest(BaseModel):
    transaction_id: str
    verification_code: str


class BlockRequest(BaseModel):
    transaction_id: str
    reason: str = "High impersonation risk"


@router.post("/check")
async def check_transaction(req: CheckTransactionRequest):
    """
    Check a transaction against VoiceGuard risk assessment.

    The backend is authoritative — frontend cannot bypass this check.
    """
    tx_request = TransactionRequest(
        transaction_id=str(uuid.uuid4()),
        transaction_type=req.transaction_type,
        amount=req.amount,
        currency=req.currency,
        beneficiary=req.beneficiary,
        requested_by=req.requested_by,
        session_id=req.session_id,
    )

    result = await banking.check_transaction(tx_request, req.risk_score, req.threshold)

    return {
        "transaction_id": result.transaction_id,
        "status": result.status,
        "risk_score": result.risk_score,
        "step_up_required": result.step_up_required,
        "step_up_method": result.step_up_method,
        "message": result.message,
    }


@router.post("/step-up")
async def request_step_up(req: StepUpRequest):
    """Request step-up verification for a blocked transaction."""
    result = await banking.request_step_up(req.transaction_id, req.method)
    return result


@router.post("/verify")
async def verify_transaction(req: VerifyRequest):
    """Verify a transaction with OTP or approval code."""
    result = await banking.approve_transaction(req.transaction_id, req.verification_code)
    return {
        "transaction_id": result.transaction_id,
        "status": result.status,
        "message": result.message,
    }


@router.post("/block")
async def block_transaction(req: BlockRequest):
    """Permanently block a transaction."""
    result = await banking.block_transaction(req.transaction_id, req.reason)
    return {
        "transaction_id": result.transaction_id,
        "status": result.status,
        "message": result.message,
    }
