"""
VoiceGuard — Demo Simulation Runner

Feeds deterministic sequences through the SAME detection → fusion → WebSocket
pipeline as real audio. This ensures the demo is not a fake frontend animation
but a genuine end-to-end system demonstration.

Usage:
    POST /api/v1/demo/simulate
    { "type": "genuine" }  or  { "type": "cloned" }

The simulation runner:
1. Creates a new call session
2. Loads the appropriate sequence
3. Feeds each window through fusion + explainability
4. Streams results via WebSocket at ~500ms intervals
"""

import asyncio
import json
import time
from typing import Optional
from datetime import datetime

from app.demo.sequences import genuine_sequence, cloned_sequence
from app.fusion.risk_engine import RiskFusionEngine, FusionConfig, get_context_threshold
from app.fusion.explainability import generate_explanations, generate_healthy_status
from app.config import settings


class SimulationRunner:
    """
    Runs a deterministic demo simulation through the real pipeline.

    Each simulation step:
    1. Reads the next window from the predefined sequence
    2. Passes scores through the fusion engine
    3. Generates explanations
    4. Produces a WebSocket message identical in format to real analysis
    """

    def __init__(self):
        self.fusion_engine = RiskFusionEngine(
            FusionConfig(
                spectral_weight=settings.spectral_weight,
                prosody_weight=settings.prosody_weight,
                speaker_weight=settings.speaker_weight,
                ema_alpha=settings.ema_alpha,
                risk_threshold=settings.default_risk_threshold,
            )
        )
        # Active simulations keyed by session_id
        self._active: dict[str, bool] = {}

    def get_sequence(self, sim_type: str) -> list[dict]:
        """Get the appropriate sequence for simulation type."""
        if sim_type == "genuine":
            return genuine_sequence()
        elif sim_type == "cloned":
            return cloned_sequence()
        else:
            raise ValueError(f"Unknown simulation type: {sim_type}. Use 'genuine' or 'cloned'.")

    async def run_simulation(
        self,
        session_id: str,
        sim_type: str,
        send_callback,
        threshold: int = 70,
        transaction_type: Optional[str] = None,
    ):
        """
        Run a full simulation, calling send_callback for each window.

        Args:
            session_id: Session ID for this simulation.
            sim_type: "genuine" or "cloned".
            send_callback: Async function to send each result (e.g., WebSocket send).
            threshold: Risk threshold for step-up decisions.
            transaction_type: Optional transaction context.
        """
        sequence = self.get_sequence(sim_type)
        self._active[session_id] = True
        self.fusion_engine.reset_session(session_id)

        try:
            for i, window in enumerate(sequence):
                # Check if simulation was stopped
                if not self._active.get(session_id, False):
                    break

                start_time = time.perf_counter()

                # Run through the real fusion engine
                fusion_result = self.fusion_engine.fuse(
                    session_id=session_id,
                    spectral_score=window["spectral"],
                    prosody_score=window["prosody"],
                    speaker_score=window["speaker"],
                    threshold_override=threshold,
                )

                # Generate explanations from the real explainability engine
                if fusion_result.fused_score > 25:
                    reasons = generate_explanations(
                        window["spectral"],
                        window["prosody"],
                        window["speaker"],
                        fusion_result.fused_score,
                    )
                else:
                    reasons = generate_healthy_status(
                        window["spectral"],
                        window["prosody"],
                        window["speaker"],
                    )

                latency_ms = (time.perf_counter() - start_time) * 1000

                # Build WebSocket message — same format as real analysis
                message = {
                    "session_id": session_id,
                    "window_index": i,
                    "ts": datetime.utcnow().isoformat(),
                    "spectral_score": window["spectral"],
                    "prosody_score": window["prosody"],
                    "speaker_match_score": window["speaker"],
                    "fused_score": fusion_result.fused_score,
                    "raw_fused_score": fusion_result.raw_fused_score,
                    "risk_state": fusion_result.risk_state,
                    "threshold": fusion_result.threshold,
                    "step_up_required": fusion_result.step_up_required,
                    "trend": fusion_result.trend,
                    "reasons": reasons,
                    "latency_ms": round(latency_ms, 1),
                    "is_demo": True,
                    "sim_type": sim_type,
                    "window_total": len(sequence),
                }

                await send_callback(json.dumps(message))

                # Wait ~500ms between windows to simulate real-time streaming
                await asyncio.sleep(0.5)

        finally:
            self._active.pop(session_id, None)

    def stop_simulation(self, session_id: str):
        """Stop a running simulation."""
        self._active[session_id] = False

    def is_running(self, session_id: str) -> bool:
        """Check if a simulation is currently running."""
        return self._active.get(session_id, False)
