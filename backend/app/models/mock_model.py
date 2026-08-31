"""
VoiceGuard — Mock Model Provider

Deterministic model provider for demo mode.
Returns consistent outputs driven by the simulation engine.
No ML weights or GPU required.

The UI clearly labels this as: MODEL STATUS — DEMO INFERENCE
"""

from app.models.base_model import BaseModelProvider


class MockModelProvider(BaseModelProvider):
    """Mock model provider for demo mode. No real ML inference."""

    def is_loaded(self) -> bool:
        return True  # Always "loaded" in demo mode

    def get_name(self) -> str:
        return "Demo Inference Engine"

    def get_status(self) -> dict:
        return {
            "mode": "demo",
            "name": self.get_name(),
            "loaded": True,
            "description": "Deterministic simulated model outputs. Not real ML inference.",
            "spectral_model": "Mock (AASIST-compatible interface)",
            "prosody_model": "Mock (Praat/librosa-compatible interface)",
            "speaker_model": "Mock (ECAPA-TDNN-compatible interface)",
        }
