"""
VoiceGuard — Risk Fusion Engine

Combines three detection signals into a single fused impersonation risk score.

Pipeline:
    spectral_score ─┐
    prosody_score  ──┼── Weighted Fusion ── EMA Smoothing ── Risk State ── Step-Up Decision
    speaker_score  ──┘

Configuration:
    - Weights are configurable (must sum to 1.0)
    - EMA alpha is configurable (higher = more responsive)
    - Risk thresholds are configurable per organization
    - Transaction-type thresholds provide context-aware decisions
"""

from dataclasses import dataclass, field
from typing import Optional
from app.config import settings


@dataclass
class FusionConfig:
    """Configuration for the risk fusion engine."""
    spectral_weight: float = 0.40
    prosody_weight: float = 0.30
    speaker_weight: float = 0.30
    ema_alpha: float = 0.3
    risk_threshold: int = 70

    def __post_init__(self):
        total = self.spectral_weight + self.prosody_weight + self.speaker_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Fusion weights must sum to 1.0, got {total}")


@dataclass
class FusionResult:
    """Output from the risk fusion engine."""
    # Raw weighted fusion score (before EMA)
    raw_fused_score: float
    # EMA-smoothed score
    fused_score: float
    # Risk state: normal | elevated | critical
    risk_state: str
    # Whether step-up verification is required
    step_up_required: bool
    # Current risk threshold used
    threshold: int
    # Score trend (change over recent windows)
    trend: float = 0.0
    # Individual contributions for transparency
    spectral_contribution: float = 0.0
    prosody_contribution: float = 0.0
    speaker_contribution: float = 0.0


class RiskFusionEngine:
    """
    Fuses multiple detection signals into a single risk score with temporal smoothing.

    The fusion is a transparent weighted combination:
        fused = w_spectral * spectral + w_prosody * prosody + w_speaker * speaker

    Followed by EMA smoothing:
        EMA_t = α * score_t + (1 - α) * EMA_(t-1)

    This prevents dashboard flickering from single anomalous windows.
    """

    def __init__(self, config: Optional[FusionConfig] = None):
        self.config = config or FusionConfig(
            spectral_weight=settings.spectral_weight,
            prosody_weight=settings.prosody_weight,
            speaker_weight=settings.speaker_weight,
            ema_alpha=settings.ema_alpha,
            risk_threshold=settings.default_risk_threshold,
        )
        # EMA state per session
        self._ema_state: dict[str, float] = {}
        # Recent scores for trend calculation
        self._recent_scores: dict[str, list[float]] = {}

    def fuse(
        self,
        session_id: str,
        spectral_score: float,
        prosody_score: float,
        speaker_score: float,
        threshold_override: Optional[int] = None,
    ) -> FusionResult:
        """
        Fuse three detection signals and apply EMA smoothing.

        Args:
            session_id: Session identifier for EMA state tracking.
            spectral_score: Spectral/deepfake detection score (0-100).
            prosody_score: Prosody irregularity score (0-100).
            speaker_score: Speaker mismatch/risk score (0-100).
            threshold_override: Optional per-org or per-transaction threshold.

        Returns:
            FusionResult with smoothed score, risk state, and step-up decision.
        """
        cfg = self.config
        threshold = threshold_override or cfg.risk_threshold

        # --- Weighted fusion ---
        spectral_contribution = cfg.spectral_weight * spectral_score
        prosody_contribution = cfg.prosody_weight * prosody_score
        speaker_contribution = cfg.speaker_weight * speaker_score
        raw_fused = spectral_contribution + prosody_contribution + speaker_contribution

        # Clamp to 0-100
        raw_fused = max(0.0, min(100.0, raw_fused))

        # --- EMA smoothing ---
        if session_id in self._ema_state:
            prev_ema = self._ema_state[session_id]
            smoothed = cfg.ema_alpha * raw_fused + (1 - cfg.ema_alpha) * prev_ema
        else:
            smoothed = raw_fused

        self._ema_state[session_id] = smoothed

        # --- Trend calculation ---
        if session_id not in self._recent_scores:
            self._recent_scores[session_id] = []
        recent = self._recent_scores[session_id]
        recent.append(smoothed)
        # Keep last 6 scores (~3 seconds at 500ms windows)
        if len(recent) > 6:
            recent.pop(0)

        trend = 0.0
        if len(recent) >= 2:
            trend = recent[-1] - recent[0]

        # --- Risk state classification ---
        risk_state = classify_risk_state(smoothed)

        # --- Step-up decision (backend is authoritative) ---
        step_up_required = smoothed >= threshold

        return FusionResult(
            raw_fused_score=round(raw_fused, 1),
            fused_score=round(smoothed, 1),
            risk_state=risk_state,
            step_up_required=step_up_required,
            threshold=threshold,
            trend=round(trend, 1),
            spectral_contribution=round(spectral_contribution, 1),
            prosody_contribution=round(prosody_contribution, 1),
            speaker_contribution=round(speaker_contribution, 1),
        )

    def reset_session(self, session_id: str):
        """Clear EMA state for a session."""
        self._ema_state.pop(session_id, None)
        self._recent_scores.pop(session_id, None)

    def get_ema(self, session_id: str) -> Optional[float]:
        """Get current EMA value for a session."""
        return self._ema_state.get(session_id)


def classify_risk_state(score: float) -> str:
    """
    Classify score into risk state.

    0-49:  normal
    50-69: elevated
    70+:   critical

    Note: the exact thresholds for step-up triggering are configurable
    per organization. This classification is for display purposes.
    """
    if score >= 70:
        return "critical"
    elif score >= 50:
        return "elevated"
    return "normal"


def get_context_threshold(
    base_threshold: int,
    transaction_type: Optional[str],
    transaction_thresholds: Optional[dict],
) -> int:
    """
    Get context-aware threshold based on transaction type.

    Higher-risk actions can apply stricter (lower) thresholds.
    """
    if transaction_type and transaction_thresholds:
        return transaction_thresholds.get(transaction_type, base_threshold)
    return base_threshold
