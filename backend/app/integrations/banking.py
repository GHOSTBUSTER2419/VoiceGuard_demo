"""
VoiceGuard — Mock Banking Integration

Simulates a banking system integration for SIH demonstration.
Demonstrates how VoiceGuard connects to real-world fraud prevention.

This mock implements:
- Transaction risk evaluation
- Step-up verification (OTP, callback, supervisor)
- Transaction approval after verification
- Transaction blocking

In production, this would be replaced with actual banking API calls.
"""

import uuid
from typing import Optional
from app.integrations.base import BaseIntegration, TransactionRequest, TransactionResult


# Mock OTP for demo — in production this would be generated and sent via SMS
DEMO_OTP = "123456"


class MockBankingIntegration(BaseIntegration):
    """
    Simulated banking integration for demo purposes.

    Demonstrates the full workflow:
    1. Transaction request received
    2. VoiceGuard risk assessment applied
    3. Step-up verification triggered if threshold exceeded
    4. Transaction approved/blocked based on verification result
    """

    def __init__(self):
        # Track pending transactions
        self._pending: dict[str, dict] = {}

    async def check_transaction(
        self,
        request: TransactionRequest,
        risk_score: float,
        threshold: int = 70,
    ) -> TransactionResult:
        """
        Evaluate a transaction against VoiceGuard risk score.

        The backend is authoritative — the frontend cannot bypass this check.
        """
        step_up_required = risk_score >= threshold

        if step_up_required:
            # Store pending transaction for later verification
            self._pending[request.transaction_id] = {
                "request": request,
                "risk_score": risk_score,
                "status": "pending_verification",
            }
            return TransactionResult(
                transaction_id=request.transaction_id,
                status="blocked",
                risk_score=risk_score,
                step_up_required=True,
                step_up_method="otp",
                message=f"Transaction blocked — impersonation risk {risk_score:.0f} exceeds threshold {threshold}. Step-up verification required.",
            )

        return TransactionResult(
            transaction_id=request.transaction_id,
            status="allowed",
            risk_score=risk_score,
            step_up_required=False,
            message="Transaction approved — voice authenticity verified.",
        )

    async def request_step_up(self, transaction_id: str, method: str = "otp") -> dict:
        """
        Initiate step-up verification.

        In production: sends OTP via SMS, initiates callback, or escalates to supervisor.
        In demo: uses predefined mock OTP.
        """
        if transaction_id not in self._pending:
            return {"success": False, "error": "Transaction not found or not pending verification."}

        self._pending[transaction_id]["step_up_method"] = method

        if method == "otp":
            return {
                "success": True,
                "method": "otp",
                "message": "OTP sent to registered mobile number.",
                "masked_number": "+91 ******4821",
                # Demo: in production, OTP would not be returned in response
            }
        elif method == "callback":
            return {
                "success": True,
                "method": "callback",
                "message": "Callback initiated to registered number.",
                "callback_id": str(uuid.uuid4())[:8],
            }
        elif method == "supervisor":
            return {
                "success": True,
                "method": "supervisor",
                "message": "Escalated to supervisor for manual review.",
                "escalation_id": str(uuid.uuid4())[:8],
            }
        else:
            return {"success": False, "error": f"Unknown verification method: {method}"}

    async def approve_transaction(
        self,
        transaction_id: str,
        verification_code: str,
    ) -> TransactionResult:
        """
        Approve a transaction after successful step-up verification.

        In demo mode, accepts the DEMO_OTP.
        In production, would validate against actual OTP/callback/supervisor approval.
        """
        if transaction_id not in self._pending:
            return TransactionResult(
                transaction_id=transaction_id,
                status="error",
                risk_score=0,
                step_up_required=False,
                message="Transaction not found or not pending verification.",
            )

        pending = self._pending[transaction_id]

        # Demo: accept the mock OTP
        if verification_code == DEMO_OTP or verification_code == "approved":
            del self._pending[transaction_id]
            return TransactionResult(
                transaction_id=transaction_id,
                status="approved_after_stepup",
                risk_score=pending["risk_score"],
                step_up_required=False,
                step_up_method=pending.get("step_up_method", "otp"),
                message="Transaction approved after step-up authentication.",
            )

        return TransactionResult(
            transaction_id=transaction_id,
            status="blocked",
            risk_score=pending["risk_score"],
            step_up_required=True,
            message="Verification failed. Transaction remains blocked.",
        )

    async def block_transaction(self, transaction_id: str, reason: str) -> TransactionResult:
        """Block a transaction permanently."""
        self._pending.pop(transaction_id, None)
        return TransactionResult(
            transaction_id=transaction_id,
            status="blocked",
            risk_score=100,
            step_up_required=False,
            message=f"Transaction permanently blocked. Reason: {reason}",
        )
