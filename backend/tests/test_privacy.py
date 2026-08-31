"""
VoiceGuard — Privacy Policy Tests

Tests that raw audio is never persisted.
"""

import pytest
from app.privacy.audio_policy import AudioPolicy, mask_phone_number, hash_identifier


class TestAudioPolicy:
    """Tests for the no-raw-audio policy."""

    def test_clean_dict_passes(self):
        data = {"spectral_score": 42.5, "prosody_score": 38.1, "risk_state": "normal"}
        assert AudioPolicy.validate_no_audio_in_dict(data) is True

    def test_audio_key_raises(self):
        data = {"audio": b"\x00\x01\x02", "score": 42.5}
        with pytest.raises(ValueError, match="PRIVACY VIOLATION"):
            AudioPolicy.validate_no_audio_in_dict(data)

    def test_raw_audio_key_raises(self):
        data = {"raw_audio": b"\x00" * 2048}
        with pytest.raises(ValueError, match="PRIVACY VIOLATION"):
            AudioPolicy.validate_no_audio_in_dict(data)

    def test_large_binary_raises(self):
        data = {"suspicous_field": b"\x00" * 2048}
        with pytest.raises(ValueError, match="PRIVACY VIOLATION"):
            AudioPolicy.validate_no_audio_in_dict(data)

    def test_small_binary_passes(self):
        data = {"small_field": b"\x00" * 100}
        assert AudioPolicy.validate_no_audio_in_dict(data) is True

    def test_consent_required(self):
        with pytest.raises(ValueError, match="consent"):
            AudioPolicy.validate_consent(False)

    def test_consent_given_passes(self):
        assert AudioPolicy.validate_consent(True) is True


class TestPhoneMasking:
    """Tests for phone number masking."""

    def test_indian_number(self):
        result = mask_phone_number("+919876543210")
        assert "3210" in result  # Last 4 digits visible
        assert "9876" not in result  # Middle digits masked

    def test_short_number(self):
        result = mask_phone_number("123")
        assert result == "****"

    def test_none_input(self):
        assert mask_phone_number(None) is None

    def test_empty_string(self):
        assert mask_phone_number("") is None


class TestIdentifierHashing:
    """Tests for sensitive identifier hashing."""

    def test_deterministic(self):
        h1 = hash_identifier("test@example.com")
        h2 = hash_identifier("test@example.com")
        assert h1 == h2

    def test_different_inputs(self):
        h1 = hash_identifier("user1")
        h2 = hash_identifier("user2")
        assert h1 != h2

    def test_length(self):
        result = hash_identifier("test")
        assert len(result) == 16
