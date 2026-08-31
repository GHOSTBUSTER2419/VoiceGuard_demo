"""
VoiceGuard — Base Model Provider

Pluggable model architecture. A configuration setting controls which
model provider is active:

    MODEL_MODE=demo       → MockModelProvider (deterministic, no weights)
    MODEL_MODE=production → Real ML model providers

The application never fails just because optional ML weights are unavailable.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseModelProvider(ABC):
    """Abstract base for model providers."""

    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if the model weights are loaded and ready."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return human-readable model name."""
        ...

    @abstractmethod
    def get_status(self) -> dict:
        """Return model status for UI display."""
        ...
