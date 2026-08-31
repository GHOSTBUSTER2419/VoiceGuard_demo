"""
VoiceGuard — Risk Fusion Engine Tests

Tests for:
- Weighted fusion calculation
- EMA smoothing
- Risk state classification
- Threshold detection
- Step-up triggering logic
"""

import pytest
from app.fusion.risk_engine import RiskFusionEngine, FusionConfig, classify_risk_state, get_context_threshold


class TestRiskFusion:
    """Tests for weighted fusion calculation."""

    def setup_method(self):
        self.engine = RiskFusionEngine(FusionConfig(
            spectral_weight=0.4,
            prosody_weight=0.3,
            speaker_weight=0.3,
            ema_alpha=1.0,  # No smoothing for pure fusion tests
            risk_threshold=70,
        ))

    def test_zero_scores(self):
        result = self.engine.fuse("test", 0, 0, 0)
        assert result.fused_score == 0.0
        assert result.risk_state == "normal"
        assert result.step_up_required is False

    def test_max_scores(self):
        result = self.engine.fuse("test", 100, 100, 100)
        assert result.fused_score == 100.0
        assert result.risk_state == "critical"
        assert result.step_up_required is True

    def test_weighted_fusion(self):
        # 0.4 * 50 + 0.3 * 50 + 0.3 * 50 = 50
        result = self.engine.fuse("test", 50, 50, 50)
        assert result.fused_score == 50.0

    def test_asymmetric_weights(self):
        # 0.4 * 100 + 0.3 * 0 + 0.3 * 0 = 40
        result = self.engine.fuse("test", 100, 0, 0)
        assert result.fused_score == 40.0

    def test_above_threshold_triggers_stepup(self):
        """CRITICAL: Score above threshold MUST trigger step_up_required."""
        result = self.engine.fuse("test", 85, 80, 75)
        assert result.fused_score >= 70
        assert result.step_up_required is True

    def test_below_threshold_no_stepup(self):
        """CRITICAL: Score below threshold MUST NOT trigger step-up."""
        result = self.engine.fuse("test", 15, 10, 12)
        assert result.fused_score < 70
        assert result.step_up_required is False

    def test_contributions_transparency(self):
        result = self.engine.fuse("test", 80, 60, 40)
        assert result.spectral_contribution == 32.0  # 0.4 * 80
        assert result.prosody_contribution == 18.0    # 0.3 * 60
        assert result.speaker_contribution == 12.0    # 0.3 * 40

    def test_threshold_override(self):
        result = self.engine.fuse("test", 60, 60, 60, threshold_override=50)
        assert result.threshold == 50
        assert result.step_up_required is True  # 60 >= 50


class TestEMASmoothing:
    """Tests for exponential moving average smoothing."""

    def test_ema_smoothing(self):
        engine = RiskFusionEngine(FusionConfig(
            spectral_weight=0.4,
            prosody_weight=0.3,
            speaker_weight=0.3,
            ema_alpha=0.3,
            risk_threshold=70,
        ))

        # First score: EMA = raw (no history)
        r1 = engine.fuse("s1", 50, 50, 50)
        assert r1.fused_score == 50.0

        # Second score: EMA = 0.3 * 80 + 0.7 * 50 = 24 + 35 = 59
        r2 = engine.fuse("s1", 80, 80, 80)
        assert abs(r2.fused_score - 59.0) < 0.2

    def test_ema_prevents_flickering(self):
        """EMA should prevent large jumps from single anomalous windows."""
        engine = RiskFusionEngine(FusionConfig(
            spectral_weight=0.4,
            prosody_weight=0.3,
            speaker_weight=0.3,
            ema_alpha=0.2,
            risk_threshold=70,
        ))

        # Establish baseline
        for _ in range(5):
            engine.fuse("s1", 20, 20, 20)

        # Single spike — should not cause full jump
        result = engine.fuse("s1", 90, 90, 90)
        assert result.fused_score < 50  # EMA should dampen the spike

    def test_separate_session_ema(self):
        engine = RiskFusionEngine(FusionConfig(ema_alpha=0.5, risk_threshold=70))
        engine.fuse("s1", 80, 80, 80)
        engine.fuse("s2", 20, 20, 20)

        # Sessions should have independent EMA state
        ema1 = engine.get_ema("s1")
        ema2 = engine.get_ema("s2")
        assert ema1 > ema2

    def test_session_reset(self):
        engine = RiskFusionEngine(FusionConfig(ema_alpha=0.5, risk_threshold=70))
        engine.fuse("s1", 80, 80, 80)
        engine.reset_session("s1")
        assert engine.get_ema("s1") is None


class TestRiskState:
    """Tests for risk state classification."""

    def test_normal_range(self):
        assert classify_risk_state(0) == "normal"
        assert classify_risk_state(25) == "normal"
        assert classify_risk_state(49) == "normal"

    def test_elevated_range(self):
        assert classify_risk_state(50) == "elevated"
        assert classify_risk_state(60) == "elevated"
        assert classify_risk_state(69) == "elevated"

    def test_critical_range(self):
        assert classify_risk_state(70) == "critical"
        assert classify_risk_state(85) == "critical"
        assert classify_risk_state(100) == "critical"


class TestContextThreshold:
    """Tests for context-aware threshold adjustment."""

    def test_no_override(self):
        assert get_context_threshold(70, None, None) == 70

    def test_transaction_override(self):
        thresholds = {"FUND_TRANSFER": 60, "GENERAL_QUERY": 80}
        assert get_context_threshold(70, "FUND_TRANSFER", thresholds) == 60
        assert get_context_threshold(70, "GENERAL_QUERY", thresholds) == 80

    def test_unknown_transaction_uses_base(self):
        thresholds = {"FUND_TRANSFER": 60}
        assert get_context_threshold(70, "UNKNOWN_TYPE", thresholds) == 70


class TestFusionWeightValidation:
    """Tests for fusion weight validation."""

    def test_valid_weights(self):
        config = FusionConfig(spectral_weight=0.4, prosody_weight=0.3, speaker_weight=0.3)
        assert config  # Should not raise

    def test_invalid_weights(self):
        with pytest.raises(ValueError):
            FusionConfig(spectral_weight=0.5, prosody_weight=0.5, speaker_weight=0.5)


class TestDemoSequenceIntegration:
    """
    Integration test: demo sequences through fusion engine.

    CRITICAL: Cloned sequence above threshold MUST trigger step_up_required.
    Genuine sequence below threshold MUST NOT trigger step-up.
    """

    def test_genuine_stays_below_threshold(self):
        from app.demo.sequences import genuine_sequence
        engine = RiskFusionEngine(FusionConfig(ema_alpha=0.3, risk_threshold=70))

        for window in genuine_sequence():
            result = engine.fuse("genuine", window["spectral"], window["prosody"], window["speaker"])

        # Final score should be well below threshold
        assert result.fused_score < 50
        assert result.step_up_required is False

    def test_cloned_exceeds_threshold(self):
        from app.demo.sequences import cloned_sequence
        engine = RiskFusionEngine(FusionConfig(ema_alpha=0.3, risk_threshold=70))

        triggered = False
        for window in cloned_sequence():
            result = engine.fuse("cloned", window["spectral"], window["prosody"], window["speaker"])
            if result.step_up_required:
                triggered = True

        # Must trigger step-up at some point
        assert triggered is True
        # Final score should be well above threshold
        assert result.fused_score > 70

    def test_cloned_transitions_through_states(self):
        from app.demo.sequences import cloned_sequence
        engine = RiskFusionEngine(FusionConfig(ema_alpha=0.3, risk_threshold=70))

        states_seen = set()
        for window in cloned_sequence():
            result = engine.fuse("cloned", window["spectral"], window["prosody"], window["speaker"])
            states_seen.add(result.risk_state)

        # Should transition through all three states
        assert "normal" in states_seen
        assert "elevated" in states_seen
        assert "critical" in states_seen
