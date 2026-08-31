"""
VoiceGuard — WebSocket Streaming Endpoint

WS /api/v1/sessions/{session_id}/stream

This is the core real-time pipeline:
1. Client connects with a session_id
2. Client sends simulation commands or audio chunks
3. Server streams back continuous risk assessments at ~500ms intervals

Message format (server → client):
{
    "session_id": "...",
    "ts": "...",
    "spectral_score": 71.2,
    "prosody_score": 67.4,
    "speaker_match_score": 31.8,
    "fused_score": 72.6,
    "risk_state": "critical",
    "threshold": 70,
    "step_up_required": true,
    "reasons": [...],
    "latency_ms": 184
}

PRIVACY: Raw audio received via WebSocket is processed in memory only
and immediately discarded after feature extraction. It is never persisted.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.demo.simulation import SimulationRunner
from app.services.session_manager import (
    get_org_config, save_feature, create_alert, end_session
)
from app.db.engine import async_session

router = APIRouter()

# Shared simulation runner instance
simulation_runner = SimulationRunner()


@router.websocket("/api/v1/sessions/{session_id}/stream")
async def session_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time voice analysis streaming.

    Clients can send:
    - {"command": "start_simulation", "type": "genuine"|"cloned"}
    - {"command": "stop"}
    - Binary audio chunks (for future real-time processing)
    """
    await websocket.accept()

    # Track state for this connection
    alert_created = False
    max_fused_score = 0.0
    final_risk_state = "normal"

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket connected. Send simulation command to begin.",
        })

        while True:
            try:
                # Wait for client message
                data = await asyncio.wait_for(websocket.receive_text(), timeout=300)
                message = json.loads(data)

                if message.get("command") == "start_simulation":
                    sim_type = message.get("type", "genuine")

                    # Get org config for threshold
                    async with async_session() as db:
                        config = await get_org_config(db, "default")
                        threshold = config.risk_threshold if config else 70
                        transaction_type = message.get("transaction_type")

                    async def send_and_store(msg_text):
                        """Send WS message and store features in DB."""
                        nonlocal alert_created, max_fused_score, final_risk_state

                        msg = json.loads(msg_text)
                        await websocket.send_text(msg_text)

                        fused = msg.get("fused_score", 0)
                        risk_state = msg.get("risk_state", "normal")

                        if fused > max_fused_score:
                            max_fused_score = fused
                        final_risk_state = risk_state

                        # Store feature scores in database
                        # PRIVACY: Only scores are stored, never raw audio
                        async with async_session() as db:
                            await save_feature(
                                db=db,
                                session_id=session_id,
                                window_index=msg.get("window_index", 0),
                                spectral_score=msg.get("spectral_score", 0),
                                prosody_score=msg.get("prosody_score", 0),
                                speaker_match_score=msg.get("speaker_match_score", 0),
                                fused_score=fused,
                                risk_state=risk_state,
                                latency_ms=msg.get("latency_ms", 0),
                                reasons=msg.get("reasons"),
                            )

                            # Create alert when risk crosses threshold (once per session)
                            if msg.get("step_up_required") and not alert_created:
                                await create_alert(
                                    db=db,
                                    session_id=session_id,
                                    org_id="default",
                                    risk_score=fused,
                                    risk_state=risk_state,
                                    transaction_type=transaction_type,
                                )
                                alert_created = True

                            await db.commit()

                    # Run the simulation through the real pipeline
                    await simulation_runner.run_simulation(
                        session_id=session_id,
                        sim_type=sim_type,
                        send_callback=send_and_store,
                        threshold=threshold,
                        transaction_type=transaction_type,
                    )

                    # Simulation complete — send end signal
                    verdict = "flagged" if max_fused_score >= threshold else "genuine"

                    # Update session in DB
                    async with async_session() as db:
                        await end_session(
                            db=db,
                            session_id=session_id,
                            final_risk_score=max_fused_score,
                            verdict=verdict,
                            step_up_triggered=alert_created,
                        )
                        await db.commit()

                    await websocket.send_json({
                        "type": "simulation_complete",
                        "session_id": session_id,
                        "final_risk_score": max_fused_score,
                        "verdict": verdict,
                        "step_up_triggered": alert_created,
                    })

                elif message.get("command") == "stop":
                    simulation_runner.stop_simulation(session_id)
                    await websocket.send_json({
                        "type": "stopped",
                        "session_id": session_id,
                    })

            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        simulation_runner.stop_simulation(session_id)
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
            })
        except Exception:
            pass
