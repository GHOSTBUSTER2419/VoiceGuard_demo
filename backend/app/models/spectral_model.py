"""VoiceGuard — Spectral Model Provider (Production Stub)

Production model for spectral/deepfake detection.
Designed to support: AASIST, RawNet2, WavLM, Wav2Vec2.

TODO: Implement real model loading and inference.
Requires: torch, torchaudio, model weights
"""
from app.models.base_model import BaseModelProvider

class SpectralModelProvider(BaseModelProvider):
    def is_loaded(self) -> bool:
        return False

    def get_name(self) -> str:
        return "AASIST / RawNet2 Spectral Detector"

    def get_status(self) -> dict:
        return {
            "mode": "production",
            "name": self.get_name(),
            "loaded": False,
            "description": "Spectral deepfake detection model. Weights not loaded.",
        }
