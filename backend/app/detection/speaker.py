"""
VoiceGuard — Speaker Consistency Analyzer

Compares current speaker embedding against enrolled voiceprint.

Production mode: Uses SpeechBrain ECAPA-TDNN to extract speaker embeddings
                 and compute cosine similarity against enrolled voiceprint.

Demo mode: Returns deterministic scores driven by simulation engine.

IMPORTANT SEMANTIC NOTE:
    High similarity to enrolled speaker → LOW impersonation risk
    Low similarity to enrolled speaker  → HIGH impersonation risk

    The returned score represents MISMATCH / RISK, not match confidence.
    speaker_match_score = 100 means "completely different from enrolled speaker"
    speaker_match_score = 0 means "identical to enrolled speaker"
"""

import time
from typing import Optional
from app.detection.base import BaseAnalyzer, DetectionResult, AnalysisContext


class SpeakerAnalyzer(BaseAnalyzer):
    """
    Speaker verification via voiceprint comparison.

    Compares current audio window embedding against enrolled voiceprint.
    Returns a RISK score (0-100):
        0 = perfect match to enrolled speaker
        100 = completely different from enrolled speaker
    """

    def get_name(self) -> str:
        return "speaker"

    async def analyze(
        self,
        audio_window: Optional[bytes],
        context: AnalysisContext,
    ) -> DetectionResult:
        """
        Compare speaker against enrolled voiceprint.

        PRIVACY: audio_window is processed in memory for embedding extraction
        only and is never persisted. Only the resulting score is stored.
        """
        start = time.perf_counter()

        if self.mode == "demo":
            result = self._demo_analyze(context)
        else:
            result = await self._production_analyze(audio_window, context)

        result.latency_ms = (time.perf_counter() - start) * 1000
        return result

    def _demo_analyze(self, context: AnalysisContext) -> DetectionResult:
        """Demo mode: baseline low risk (high match) for non-simulated calls."""
        return DetectionResult(
            score=8.0,  # Low score = high match = low risk
            confidence=0.90,
            reasons=[],
            features={"mode": "demo", "analyzer": "speaker"},
        )

    async def _production_analyze(
        self,
        audio_window: Optional[bytes],
        context: AnalysisContext,
    ) -> DetectionResult:
        """
        Production mode: extract embedding and compare to enrolled voiceprint.

        TODO: Implement real speaker verification:
        1. Extract speaker embedding using ECAPA-TDNN
        2. If enrolled_embedding exists in context, compute cosine similarity
        3. Convert similarity to risk score (high sim → low risk)
        4. If no enrolled voiceprint, return neutral score with explanation
        """
        if context.enrolled_embedding is None:
            return DetectionResult(
                score=50.0,  # Neutral — no voiceprint to compare against
                confidence=0.0,
                reasons=[{
                    "id": "no_voiceprint",
                    "title": "No enrolled voiceprint available",
                    "severity": "info",
                }],
                features={"mode": "production", "voiceprint_available": False},
            )

        return DetectionResult(
            score=0.0,
            confidence=0.0,
            reasons=[{"id": "speaker_unavailable", "title": "Speaker model not loaded", "severity": "info"}],
            features={"mode": "production", "model_loaded": False},
        )


def create_speaker_reasons(score: float) -> list[dict]:
    """
    Generate human-readable reasons based on speaker mismatch score.

    Remember: high score = high mismatch = high risk.
    """
    reasons = []

    if score > 60:
        reasons.append({
            "id": "voiceprint_mismatch",
            "title": "Voiceprint mismatch detected",
            "description": "Current speaker embedding differs significantly from enrolled voiceprint.",
            "severity": "high",
            "signal_source": "speaker",
            "active": True,
        })

    if score > 40:
        reasons.append({
            "id": "speaker_drift",
            "title": "Speaker consistency drift",
            "description": "Intra-session speaker characteristics show unusual variation.",
            "severity": "medium" if score <= 60 else "high",
            "signal_source": "speaker",
            "active": True,
        })

    if score > 75:
        reasons.append({
            "id": "identity_conflict",
            "title": "Possible identity conflict",
            "description": "Voice characteristics are inconsistent with the claimed caller identity.",
            "severity": "critical",
            "signal_source": "speaker",
            "active": True,
        })

    return reasons
