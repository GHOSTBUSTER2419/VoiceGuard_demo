"""
VoiceGuard — Application Configuration

All configuration is loaded from environment variables.
No secrets are hard-coded. See .env.example for reference.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Central configuration for VoiceGuard backend."""

    # --- Application ---
    app_name: str = "VoiceGuard"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "info"

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    # Empty string = auth disabled (development mode)
    voiceguard_api_key: str = ""

    # --- Model Mode ---
    # "demo" = deterministic simulated scores (no ML weights needed)
    # "production" = real ML model inference
    model_mode: str = "demo"

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./voiceguard.db"

    # --- Redis ---
    # Empty = in-memory fallback
    redis_url: str = ""

    # --- Risk Thresholds ---
    default_risk_threshold: int = 70
    default_workflow: str = "otp"  # otp | callback | supervisor

    # --- Fusion Weights (must sum to 1.0) ---
    spectral_weight: float = 0.40
    prosody_weight: float = 0.30
    speaker_weight: float = 0.30

    # --- EMA Smoothing ---
    # α: higher = more responsive, lower = smoother
    ema_alpha: float = 0.3

    # --- Session ---
    session_ttl_seconds: int = 3600

    # --- Privacy ---
    feature_retention_days: int = 90
    audit_enabled: bool = True

    @property
    def is_demo_mode(self) -> bool:
        return self.model_mode == "demo"

    @property
    def auth_enabled(self) -> bool:
        return bool(self.voiceguard_api_key)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()
