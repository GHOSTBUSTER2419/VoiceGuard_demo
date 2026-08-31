"""
VoiceGuard — Python SDK Example

Demonstrates how an external banking application can:
1. Create a VoiceGuard session
2. Stream data via WebSocket
3. Receive real-time risk updates
4. React to step_up_required signals

Usage:
    pip install httpx websockets
    python python_client.py

Prerequisites:
    VoiceGuard backend running at http://localhost:8000
"""

import asyncio
import json
import httpx
import websockets

API_BASE = "http://localhost:8000/api/v1"
WS_BASE = "ws://localhost:8000/api/v1"


async def main():
    print("[VoiceGuard SDK] Starting demo client...\n")

    # --- Step 1: Create a session ---
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE}/demo/simulate", json={
            "type": "cloned",
            "org_id": "default",
            "transaction_type": "FUND_TRANSFER",
            "transaction_value": 250000,
            "speaker_label": "CFO - Rajesh Kumar",
        })
        data = response.json()
        session_id = data["session_id"]
        print(f"[Session Created] ID: {session_id}")
        print(f"[Session Created] Type: cloned simulation")
        print()

    # --- Step 2: Connect via WebSocket ---
    uri = f"{WS_BASE}/sessions/{session_id}/stream"
    print(f"[WebSocket] Connecting to {uri}...")

    async with websockets.connect(uri) as ws:
        # Wait for connection confirmation
        msg = await ws.recv()
        print(f"[WebSocket] Connected: {json.loads(msg).get('message')}\n")

        # --- Step 3: Start simulation ---
        await ws.send(json.dumps({
            "command": "start_simulation",
            "type": "cloned",
        }))

        print("[Streaming] Receiving real-time risk updates...\n")
        print(f"{'Window':>6} | {'Spectral':>8} | {'Prosody':>8} | {'Speaker':>8} | {'Fused':>6} | {'State':>10} | Step-Up")
        print("-" * 80)

        # --- Step 4: Receive risk updates ---
        step_up_alerted = False

        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=30)
                data = json.loads(raw)

                # Skip non-score messages
                if data.get("type") in ("ping", "connected"):
                    continue

                if data.get("type") == "simulation_complete":
                    print(f"\n[Complete] Final risk: {data.get('final_risk_score', 0):.0f}")
                    print(f"[Complete] Verdict: {data.get('verdict', 'unknown')}")
                    break

                # Display score update
                print(
                    f"{data.get('window_index', 0):>6} | "
                    f"{data.get('spectral_score', 0):>8.1f} | "
                    f"{data.get('prosody_score', 0):>8.1f} | "
                    f"{data.get('speaker_match_score', 0):>8.1f} | "
                    f"{data.get('fused_score', 0):>6.1f} | "
                    f"{data.get('risk_state', ''):>10} | "
                    f"{'YES' if data.get('step_up_required') else 'no'}"
                )

                # --- React to step-up requirement ---
                if data.get("step_up_required") and not step_up_alerted:
                    step_up_alerted = True
                    print(f"\n[ALERT] Step-up verification required!")
                    print(f"[ALERT] Risk score: {data['fused_score']:.0f}")
                    print(f"[ALERT] Threshold: {data['threshold']}")

                    # In a real integration, you would:
                    # 1. Block the pending transaction
                    # 2. Send OTP to registered number
                    # 3. Wait for verification
                    # 4. Approve or reject based on verification result
                    print(f"[ACTION] Transaction BLOCKED pending verification\n")

            except asyncio.TimeoutError:
                break

    print("\n[VoiceGuard SDK] Demo complete.")


if __name__ == "__main__":
    asyncio.run(main())
