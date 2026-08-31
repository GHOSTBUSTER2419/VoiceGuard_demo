"""
VoiceGuard — Demo Simulation Tests

Tests that demo sequences produce correct risk trajectories.
"""

import pytest
from app.demo.sequences import genuine_sequence, cloned_sequence


class TestGenuineSequence:
    """Tests for the genuine call simulation sequence."""

    def test_sequence_not_empty(self):
        seq = genuine_sequence()
        assert len(seq) > 0

    def test_all_scores_low(self):
        for window in genuine_sequence():
            assert window["spectral"] <= 30
            assert window["prosody"] <= 30
            assert window["speaker"] <= 20

    def test_has_required_keys(self):
        for window in genuine_sequence():
            assert "spectral" in window
            assert "prosody" in window
            assert "speaker" in window


class TestClonedSequence:
    """Tests for the cloned call simulation sequence."""

    def test_sequence_not_empty(self):
        seq = cloned_sequence()
        assert len(seq) > 0

    def test_starts_low(self):
        seq = cloned_sequence()
        assert seq[0]["spectral"] < 30
        assert seq[0]["prosody"] < 30

    def test_ends_high(self):
        seq = cloned_sequence()
        last = seq[-1]
        assert last["spectral"] > 70
        assert last["prosody"] > 70
        assert last["speaker"] > 70

    def test_monotonically_increasing_trend(self):
        """Overall trend should be increasing (though local dips are ok)."""
        seq = cloned_sequence()
        # Compare first quarter average to last quarter average
        q1 = seq[:len(seq)//4]
        q4 = seq[-(len(seq)//4):]

        avg_q1 = sum(w["spectral"] for w in q1) / len(q1)
        avg_q4 = sum(w["spectral"] for w in q4) / len(q4)
        assert avg_q4 > avg_q1

    def test_deterministic(self):
        """Sequences must be deterministic (reproducible for SIH demo)."""
        s1 = cloned_sequence()
        s2 = cloned_sequence()
        assert s1 == s2
