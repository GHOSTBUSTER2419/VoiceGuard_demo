"""
VoiceGuard — Detection Base Classes

Defines the common interface for all detection analyzers.
Every analyzer (spectral, prosody, speaker) implements this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DetectionResult:
    """Result from a single detection analyzer for one audio window."""
    # Score 0-100: higher = more suspicious / anomalous
    score: float
    # Confidence in the score (0.0-1.0)
    confidence: float = 1.0
    # Human-readable reasons for the score
    reasons: list[dict] = field(default_factory=list)
    # Extracted features (for storage/debugging, never raw audio)
    features: dict = field(default_factory=dict)
    # Processing latency in milliseconds
    latency_ms: float = 0.0


@dataclass
class AnalysisContext:
    """Context passed to analyzers for each audio window."""
    session_id: str
    window_index: int
    language: str = "en"
    accent_profile: Optional[str] = None
    transaction_type: Optional[str] = None
    # Enrolled voiceprint embedding for speaker comparison
    enrolled_embedding: Optional[list[float]] = None
    # Whether this is a demo/simulation run
    is_demo: bool = False
    # Previous scores for temporal analysis
    previous_scores: list[float] = field(default_factory=list)


class BaseAnalyzer(ABC):
    """
    Abstract base class for all VoiceGuard detection analyzers.

    Each analyzer processes an audio window and returns a DetectionResult.
    In demo mode, analyzers use deterministic mock outputs.
    In production mode, they invoke real ML models.
    """

    def __init__(self, mode: str = "demo"):
        self.mode = mode

    @abstractmethod
    async def analyze(
        self,
        audio_window: Optional[bytes],
        context: AnalysisContext,
    ) -> DetectionResult:
        """
        Analyze a single audio window.

        Args:
            audio_window: Raw audio bytes for this window (processed in memory only).
                          In demo mode, this may be None.
                          PRIVACY: This data must NEVER be persisted.
            context: Analysis context including session info and enrolled voiceprint.

        Returns:
            DetectionResult with score, confidence, reasons, and features.
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the analyzer name (e.g., 'spectral', 'prosody', 'speaker')."""
        ...
