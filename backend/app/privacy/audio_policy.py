"""
VoiceGuard — Audio Privacy Policy

PRIVACY BY DESIGN — First-Class Architectural Component

This module enforces VoiceGuard's strict audio privacy policy:

1. Raw audio is processed IN MEMORY ONLY for feature extraction
2. Raw audio must NOT be written to disk (filesystem, temp files)
3. Raw audio must NOT be inserted into PostgreSQL
4. Raw audio must NOT be stored in Redis
5. Raw audio must NOT appear in application logs
6. Voiceprints require EXPLICIT CONSENT before enrollment
7. Stored voiceprints are EMBEDDINGS — never recordings
8. Call origin should be MASKED or HASHED
9. Feature retention is CONFIGURABLE
10. All operations include AUDIT METADATA

This policy applies to all components: ingestion, detection, storage, caching, and logging.
"""

import hashlib
import re
from typing import Optional
from app.config import settings


class AudioPolicy:
    """
    Enforces the no-raw-audio-persistence policy.

    Use this class to validate that audio data is handled correctly
    throughout the processing pipeline.
    """

    @staticmethod
    def validate_no_audio_in_dict(data: dict, context: str = "") -> bool:
        """
        Validate that a dictionary does not contain raw audio data.
        Used before persisting data to database or cache.

        Raises ValueError if raw audio is detected.
        """
        forbidden_keys = {"audio", "raw_audio", "audio_data", "audio_bytes", "waveform_raw", "pcm_data"}

        for key in data.keys():
            if key.lower() in forbidden_keys:
                raise ValueError(
                    f"PRIVACY VIOLATION: Attempted to persist raw audio via key '{key}' "
                    f"in context '{context}'. Raw audio must never be stored. "
                    f"Only scores, embeddings, and metadata are permitted."
                )

            # Check for large binary values that might be audio
            value = data[key]
            if isinstance(value, (bytes, bytearray)) and len(value) > 1024:
                raise ValueError(
                    f"PRIVACY VIOLATION: Large binary data ({len(value)} bytes) found "
                    f"in key '{key}' in context '{context}'. "
                    f"This may be raw audio data. Only embeddings and scores are permitted."
                )

        return True

    @staticmethod
    def validate_consent(consent_given: bool, context: str = "") -> bool:
        """
        Validate that explicit consent has been given before voiceprint enrollment.

        Raises ValueError if consent is not provided.
        """
        if not consent_given:
            raise ValueError(
                f"PRIVACY VIOLATION: Voiceprint enrollment attempted without explicit consent "
                f"in context '{context}'. Enrollment requires consent_given=True."
            )
        return True


def mask_phone_number(phone: Optional[str]) -> Optional[str]:
    """
    Mask a phone number for storage and display.

    Example: +91 9876543210 → +91 ******3210

    Raw phone numbers should not be stored in cleartext.
    """
    if not phone:
        return None

    # Remove non-digit characters except leading +
    digits = re.sub(r"[^\d+]", "", phone)

    if len(digits) < 4:
        return "****"

    # Keep country code prefix and last 4 digits
    if digits.startswith("+"):
        # Find where country code ends (assume 2-3 digit country code)
        prefix = digits[:3] if len(digits) > 10 else digits[:2]
        suffix = digits[-4:]
        masked_middle = "*" * (len(digits) - len(prefix) - 4)
        return f"{prefix} {masked_middle}{suffix}"
    else:
        suffix = digits[-4:]
        masked_middle = "*" * (len(digits) - 4)
        return f"{masked_middle}{suffix}"


def hash_identifier(value: str) -> str:
    """
    Hash a sensitive identifier for storage.
    Used for call origins and other PII that needs to be stored
    in a way that prevents direct identification.
    """
    return hashlib.sha256(value.encode()).hexdigest()[:16]
