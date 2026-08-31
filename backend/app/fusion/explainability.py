"""
VoiceGuard — Explainability Engine

Generates structured, human-readable explanations for why VoiceGuard
flags a call as suspicious. Explanations are rule-based and map directly
to detection sub-scores.

Each reason has:
    - id: unique identifier
    - title: short human-readable label
    - description: detailed explanation
    - severity: low | medium | high | critical
    - signal_source: spectral | prosody | speaker | fusion
    - active: whether the reason is currently triggered

The frontend renders these as collapsible explanation cards.
"""

from app.detection.spectral import create_spectral_reasons
from app.detection.prosody import create_prosody_reasons
from app.detection.speaker import create_speaker_reasons


def generate_explanations(
    spectral_score: float,
    prosody_score: float,
    speaker_score: float,
    fused_score: float,
) -> list[dict]:
    """
    Generate all active explanation reasons from sub-scores.

    Returns a list of reason dicts sorted by severity (critical first).
    """
    reasons = []

    # Collect reasons from each analyzer
    reasons.extend(create_spectral_reasons(spectral_score))
    reasons.extend(create_prosody_reasons(prosody_score))
    reasons.extend(create_speaker_reasons(speaker_score))

    # Add fusion-level reasons
    reasons.extend(_create_fusion_reasons(
        spectral_score, prosody_score, speaker_score, fused_score
    ))

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    reasons.sort(key=lambda r: severity_order.get(r.get("severity", "info"), 5))

    return reasons


def generate_healthy_status(
    spectral_score: float,
    prosody_score: float,
    speaker_score: float,
) -> list[dict]:
    """
    Generate positive status indicators for healthy signals.
    Shown when sub-scores are below concern thresholds.
    """
    healthy = []

    if spectral_score <= 30:
        healthy.append({
            "id": "spectral_ok",
            "title": "Spectral consistency verified",
            "severity": "ok",
            "signal_source": "spectral",
            "active": True,
        })

    if prosody_score <= 30:
        healthy.append({
            "id": "prosody_ok",
            "title": "Natural prosody patterns",
            "severity": "ok",
            "signal_source": "prosody",
            "active": True,
        })

    if speaker_score <= 30:
        healthy.append({
            "id": "speaker_ok",
            "title": "Speaker identity consistent",
            "severity": "ok",
            "signal_source": "speaker",
            "active": True,
        })

    return healthy


def _create_fusion_reasons(
    spectral_score: float,
    prosody_score: float,
    speaker_score: float,
    fused_score: float,
) -> list[dict]:
    """Generate fusion-level reasons when multiple signals converge."""
    reasons = []

    # Count how many signals are above concern threshold
    elevated_count = sum(1 for s in [spectral_score, prosody_score, speaker_score] if s > 50)

    if elevated_count >= 3:
        reasons.append({
            "id": "multi_signal_convergence",
            "title": "Multiple authenticity signals converging",
            "description": "All three detection signals indicate elevated risk simultaneously.",
            "severity": "critical",
            "signal_source": "fusion",
            "active": True,
        })
    elif elevated_count >= 2:
        reasons.append({
            "id": "dual_signal_alert",
            "title": "Correlated detection signals",
            "description": "Two independent detection signals show elevated anomaly scores.",
            "severity": "high",
            "signal_source": "fusion",
            "active": True,
        })

    if fused_score > 80:
        reasons.append({
            "id": "extreme_risk",
            "title": "Extreme impersonation risk",
            "description": "Fused risk score exceeds 80. Immediate verification strongly recommended.",
            "severity": "critical",
            "signal_source": "fusion",
            "active": True,
        })

    return reasons
