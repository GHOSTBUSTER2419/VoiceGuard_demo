"""
VoiceGuard — Integration Base

Abstract base for external system integrations.
Designed to support: banking, contact centers, telecom, enterprise collaboration.

Future adapters: Asterisk, FreeSWITCH, Genesys, Teams, Zoom,
SIP media servers, core banking IVR.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class TransactionRequest:
    """A transaction that requires VoiceGuard risk assessment."""
    transaction_id: str
    transaction_type: str  # FUND_TRANSFER, PAYROLL_CHANGE, etc.
    amount: Optional[float] = None
    currency: str = "INR"
    beneficiary: Optional[str] = None
    requested_by: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class TransactionResult:
    """Result of a transaction risk assessment."""
    transaction_id: str
    # allowed | blocked | pending_verification | approved_after_stepup
    status: str
    risk_score: float
    step_up_required: bool
    step_up_method: Optional[str] = None
    message: str = ""


class BaseIntegration(ABC):
    """Abstract base for all VoiceGuard integrations."""

    @abstractmethod
    async def check_transaction(self, request: TransactionRequest, risk_score: float) -> TransactionResult:
        """Evaluate whether a transaction should proceed given the risk score."""
        ...

    @abstractmethod
    async def request_step_up(self, transaction_id: str, method: str) -> dict:
        """Request step-up verification for a transaction."""
        ...

    @abstractmethod
    async def approve_transaction(self, transaction_id: str, verification_code: str) -> TransactionResult:
        """Approve a transaction after successful step-up verification."""
        ...

    @abstractmethod
    async def block_transaction(self, transaction_id: str, reason: str) -> TransactionResult:
        """Block a transaction due to high risk."""
        ...
