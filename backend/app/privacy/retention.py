"""
VoiceGuard — Data Retention Policy

Configurable retention for feature data and audit metadata.
Raw audio is never retained — this module governs retention
of scores, embeddings, alerts, and session metadata.
"""

from datetime import datetime, timedelta
from app.config import settings


class RetentionPolicy:
    """Manages data retention rules for VoiceGuard stored data."""

    def __init__(self, retention_days: int = None):
        self.retention_days = retention_days or settings.feature_retention_days

    @property
    def retention_cutoff(self) -> datetime:
        """Get the datetime before which data should be purged."""
        return datetime.utcnow() - timedelta(days=self.retention_days)

    def should_retain(self, created_at: datetime) -> bool:
        """Check if a record should be retained based on its creation date."""
        return created_at > self.retention_cutoff

    def get_audit_metadata(self) -> dict:
        """
        Generate audit metadata for data operations.
        Included with stored records for compliance tracking.
        """
        return {
            "retention_policy_days": self.retention_days,
            "audit_enabled": settings.audit_enabled,
            "policy_applied_at": datetime.utcnow().isoformat(),
            "raw_audio_stored": False,  # Always false — by design
        }
