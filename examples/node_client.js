/**
 * VoiceGuard — Node.js SDK Example
 *
 * Demonstrates WebSocket integration from a Node.js application.
 *
 * Usage:
 *   npm install ws node-fetch
 *   node node_client.js
 *
 * Prerequisites:
 *   VoiceGuard backend running at http://localhost:8000
 */

const WebSocket = require('ws');

const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE = 'ws://localhost:8000/api/v1';

async function main() {
  console.log('[VoiceGuard SDK] Starting Node.js demo client...\n');

  // Step 1: Create session via REST API
  const response = await fetch(`${API_BASE}/demo/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: 'cloned',
      org_id: 'default',
      transaction_type: 'FUND_TRANSFER',
      transaction_value: 250000,
      speaker_label: 'CFO - Rajesh Kumar',
    }),
  });

  const data = await response.json();
  const sessionId = data.session_id;
  console.log(`[Session Created] ID: ${sessionId}\n`);

  // Step 2: Connect via WebSocket
  const ws = new WebSocket(`${WS_BASE}/sessions/${sessionId}/stream`);

  ws.on('open', () => {
    console.log('[WebSocket] Connected\n');

    // Step 3: Start simulation
    ws.send(JSON.stringify({
      command: 'start_simulation',
      type: 'cloned',
    }));
  });

  let stepUpAlerted = false;

  ws.on('message', (raw) => {
    const msg = JSON.parse(raw.toString());

    if (msg.type === 'connected' || msg.type === 'ping') return;

    if (msg.type === 'simulation_complete') {
      console.log(`\n[Complete] Final risk: ${msg.final_risk_score}`);
      console.log(`[Complete] Verdict: ${msg.verdict}`);
      ws.close();
      return;
    }

    if (msg.fused_score !== undefined) {
      const line = [
        `Window ${String(msg.window_index).padStart(3)}`,
        `Fused: ${msg.fused_score.toFixed(1).padStart(5)}`,
        `State: ${msg.risk_state.padEnd(8)}`,
        `StepUp: ${msg.step_up_required ? 'YES' : 'no'}`,
      ].join(' | ');
      console.log(line);

      // Step 4: React to step-up
      if (msg.step_up_required && !stepUpAlerted) {
        stepUpAlerted = true;
        console.log(`\n[ALERT] Step-up verification required!`);
        console.log(`[ALERT] Risk: ${msg.fused_score} | Threshold: ${msg.threshold}`);
        console.log(`[ACTION] Block transaction pending verification\n`);
      }
    }
  });

  ws.on('close', () => {
    console.log('\n[VoiceGuard SDK] Connection closed.');
  });

  ws.on('error', (err) => {
    console.error('[WebSocket Error]', err.message);
  });
}

main().catch(console.error);
