"""VoiceGuard — Speaker Model Provider (Production Stub)

Production model for speaker verification.
Designed to use: SpeechBrain ECAPA-TDNN.

TODO: Implement real speaker embedding extraction and comparison.
Requires: speechbrain, torch, torchaudio
"""
from app.models.base_model import BaseModelProvider

class SpeakerModelProvider(BaseModelProvider):
    def is_loaded(self) -> bool:
        return False

    def get_name(self) -> str:
        return "SpeechBrain ECAPA-TDNN Speaker Verifier"

    def get_status(self) -> dict:
        return {
            "mode": "production",
            "name": self.get_name(),
            "loaded": False,
            "description": "Speaker verification using ECAPA-TDNN embeddings. Not loaded.",
        }
