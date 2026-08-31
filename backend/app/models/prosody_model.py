"""VoiceGuard — Prosody Model Provider (Production Stub)

Production model for prosody analysis.
Designed to use: parselmouth (Praat), librosa.

TODO: Implement real F0 extraction, jitter/shimmer analysis.
Requires: parselmouth, librosa, numpy
"""
from app.models.base_model import BaseModelProvider

class ProsodyModelProvider(BaseModelProvider):
    def is_loaded(self) -> bool:
        return False

    def get_name(self) -> str:
        return "Praat / Librosa Prosody Analyzer"

    def get_status(self) -> dict:
        return {
            "mode": "production",
            "name": self.get_name(),
            "loaded": False,
            "description": "Prosody analysis using parselmouth and librosa. Not loaded.",
        }
