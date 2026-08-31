# VoiceGuard

**AI-Powered Real-Time Voice Cloning & Impersonation Detection**

> SIH Problem Statement: SIH26104 — AI-Powered Real-Time Detection and Prevention of Voice Cloning Impersonation Attacks

---

## What is VoiceGuard?

VoiceGuard is a real-time security layer that continuously analyzes incoming speech during live calls to detect voice cloning and impersonation attacks. Unlike batch-processing systems, VoiceGuard analyzes audio in **streaming 500ms windows** and updates an impersonation risk score approximately every half-second.

When risk exceeds a configurable threshold, VoiceGuard automatically triggers **step-up verification** (OTP, callback, or supervisor approval) to prevent fraudulent transactions before they happen.

**Demo mode uses deterministic simulated model outputs. Production mode is designed for real detection models.**

---

## Architecture

```
CALL AUDIO
   ↓
STREAMING INGESTION (WebSocket)
   ↓
MULTI-SIGNAL ANALYSIS
   ├── Spectral / Deepfake Artifacts
   ├── Prosody Irregularities
   └── Speaker Voiceprint Consistency
   ↓
RISK FUSION ENGINE (Weighted + EMA)
   ↓
0–100 IMPERSONATION RISK SCORE
   ↓
CONTEXT-AWARE DECISION
   ↓
NORMAL / ELEVATED / CRITICAL
   ↓
STEP-UP VERIFICATION
   ↓
ALLOW / VERIFY / ESCALATE / BLOCK
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Real-Time Streaming** | 500ms analysis windows with continuous risk scoring |
| **Multi-Signal Detection** | Spectral, prosody, and speaker consistency analysis |
| **Risk Fusion** | Weighted combination with EMA temporal smoothing |
| **Step-Up Verification** | OTP, callback, and supervisor escalation workflows |
| **Banking Integration** | Mock transaction blocking and approval workflow |
| **Explainability** | Human-readable reasons for each risk assessment |
| **Privacy by Design** | Raw audio is never persisted — only embeddings and scores |
| **Configurable Policies** | Per-organization thresholds and workflows |
| **Voiceprint Enrollment** | Consent-based speaker identity registration |
| **Demo Simulation** | Deterministic sequences for reproducible demonstrations |
| **API Documentation** | Auto-generated OpenAPI docs at `/docs` |
| **Docker Support** | Full Docker Compose with PostgreSQL and Redis |
| **SDK Examples** | Python and Node.js integration examples |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | SQLite (dev) / PostgreSQL 16 + pgvector (Docker) |
| Cache | In-memory (dev) / Redis 7 (Docker) |
| WebSocket | FastAPI WebSocket + websockets |
| Frontend | React 18, Vite 5, Recharts, Lucide React |
| ML (Production) | AASIST, RawNet2, WavLM, parselmouth, SpeechBrain ECAPA-TDNN |
| Containerization | Docker, Docker Compose |

---

## Local Setup (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Access

- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Docker Setup

```bash
# Copy environment file
cp .env.example .env

# Build and start all services
docker compose up --build

# Access
# Dashboard: http://localhost:5173
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Demo Instructions

### 2-Minute SIH Demo Script

**Scene 1 — Genuine Call (30 seconds)**

1. Open the dashboard at http://localhost:5173
2. Observe: **SYSTEM ONLINE**, **WS CONNECTED**, **MODEL: DEMO**
3. Click **SIMULATE GENUINE CALL**
4. Watch: Risk score stays 10-30, status **NORMAL**
5. Waveform moves, all three signal traces stay low
6. Explainability shows green checkmarks

**Scene 2 — Cloned Call (60 seconds)**

1. Click **SIMULATE CLONED CALL**
2. Watch scores escalate: NORMAL → ELEVATED → CRITICAL
3. Signal traces rise: spectral, prosody, and speaker
4. Explainability panel activates warnings:
   - "Spectral discontinuity detected"
   - "Unnatural pitch flatness"
   - "Voiceprint mismatch detected"
5. Risk gauge animates from blue → amber → red

**Scene 3 — Step-Up Security (30 seconds)**

1. When risk exceeds threshold (70), a security overlay appears
2. Shows: risk score, threshold, transaction details
3. Click **SEND OTP VERIFICATION**
4. Enter demo OTP: `123456`
5. Click **VERIFY**
6. Overlay shows: **STEP-UP VERIFIED — Transaction can proceed**
7. Banking card shows: **APPROVED AFTER STEP-UP AUTHENTICATION**

**Scene 4 — Review (30 seconds)**

1. Alert timeline shows the flagged session
2. Expand alert to see sub-score details
3. Submit analyst feedback: True Positive or False Positive
4. Show configurable threshold slider and workflow selector

---

## API Documentation

Interactive API docs available at: **http://localhost:8000/docs**

### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/sessions` | Create call session |
| `GET` | `/api/v1/sessions/{id}` | Get session with score history |
| `WS` | `/api/v1/sessions/{id}/stream` | Real-time streaming |
| `POST` | `/api/v1/voiceprints` | Enroll voiceprint (requires consent) |
| `GET` | `/api/v1/orgs/{id}/config` | Get org risk configuration |
| `PUT` | `/api/v1/orgs/{id}/config` | Update org risk configuration |
| `GET` | `/api/v1/alerts` | List alerts (paginated) |
| `POST` | `/api/v1/alerts/{id}/feedback` | Submit analyst feedback |
| `POST` | `/api/v1/demo/simulate` | Trigger demo simulation |
| `POST` | `/api/v1/banking/check` | Check transaction risk |
| `POST` | `/api/v1/banking/step-up` | Request step-up verification |
| `POST` | `/api/v1/banking/verify` | Verify OTP/approval code |

### WebSocket Protocol

**Connect**: `ws://localhost:8000/api/v1/sessions/{session_id}/stream`

**Client → Server**:
```json
{"command": "start_simulation", "type": "genuine|cloned"}
{"command": "stop"}
```

**Server → Client**:
```json
{
  "session_id": "...",
  "ts": "2024-01-01T00:00:00",
  "spectral_score": 71.2,
  "prosody_score": 67.4,
  "speaker_match_score": 31.8,
  "fused_score": 72.6,
  "risk_state": "critical",
  "threshold": 70,
  "step_up_required": true,
  "trend": 14.2,
  "reasons": [
    {"id": "prosody_flatness", "title": "Unnatural pitch flatness", "severity": "high"}
  ],
  "latency_ms": 2.1,
  "is_demo": true
}
```

---

## Privacy Architecture

VoiceGuard implements **Privacy by Design** as a first-class architectural component:

1. **Raw audio is processed in memory only** — never written to disk, database, cache, or logs
2. **Voiceprints require explicit consent** — `consent_given` must be `true`
3. **Voiceprints are embeddings** — mathematical vectors, not recordings
4. **Call origin is masked** — `+91 ******4821`
5. **Feature retention is configurable** — default 90 days
6. **Audit metadata** is included with all stored records
7. **Privacy validation** runs before any data persistence

The `AudioPolicy` class enforces these rules programmatically and raises `ValueError` on any violation attempt.

---

## Model Architecture

VoiceGuard uses a pluggable model provider system:

| Setting | Behavior |
|---------|----------|
| `MODEL_MODE=demo` | Deterministic simulated scores (no weights needed) |
| `MODEL_MODE=production` | Real ML model inference |

### Production Models (when integrated)

| Signal | Model | Library |
|--------|-------|---------|
| Spectral | AASIST / RawNet2 / WavLM | PyTorch, torchaudio |
| Prosody | F0 extraction, jitter/shimmer | parselmouth, librosa |
| Speaker | ECAPA-TDNN embeddings | SpeechBrain |

### Training Datasets (for future development)

- ASVspoof 2019 LA
- ASVspoof 2021 LA
- In-the-Wild
- WaveFake
- FoR (Fake-or-Real)

---

## Multilingual Roadmap

The system architecture supports multilingual operation:

- Language is a session parameter (`language`, `accent_profile`)
- Detection uses language-agnostic acoustic/prosodic features
- No language-specific assumptions in the detection pipeline
- Demo metadata includes Hindi and Indian-accented English
- Planned support: Hindi, English (Indian accents), major regional languages

**Note**: Multilingual accuracy has not been validated in this prototype. Production deployment would require language-specific model validation.

---

## Integration Architecture

VoiceGuard provides a clean API boundary for integration with:

| System | Status |
|--------|--------|
| Banking / Core Banking IVR | ✅ Mock implementation |
| Contact Centers (Genesys, Avaya) | 📋 Interface defined |
| Telecom (Asterisk, FreeSWITCH, SIP) | 📋 Interface defined |
| Enterprise (Teams, Zoom) | 📋 Planned |
| Government Systems | 📋 Planned |

See `examples/python_client.py` and `examples/node_client.js` for SDK usage.

---

## Known Limitations

1. **Demo mode only** — No real ML inference in the prototype
2. **No real audio processing** — Browser microphone integration not implemented
3. **SQLite in local dev** — Switch to PostgreSQL for production
4. **In-memory cache** — Switch to Redis for production
5. **No real OTP delivery** — Uses mock OTP (`123456`)
6. **No multilingual validation** — Architecture supports it, accuracy not tested
7. **No model metrics** — No EER/accuracy claims without real validation
8. **Single-organization** — Multi-tenancy not fully implemented

---

## Future Scope

1. **Real ML models** — AASIST, parselmouth, ECAPA-TDNN integration
2. **Browser microphone** — WebRTC audio capture and streaming
3. **Continual learning** — Analyst feedback → model retraining loop
4. **Multi-tenancy** — Full organization isolation
5. **SIP/telecom integration** — Asterisk/FreeSWITCH media servers
6. **Kubernetes deployment** — Production-grade orchestration
7. **Model validation** — ASVspoof benchmarks, EER measurement
8. **Multilingual models** — Hindi, Tamil, Telugu, Bengali accent models
9. **Real-time alerting** — Email/SMS/webhook notifications
10. **Compliance dashboard** — CERT-In, RBI regulatory reporting

---

## SIH Demo Script (Detailed)

### Setup
```bash
# Start the system
cd voiceguard
docker compose up --build
# OR locally:
# Terminal 1: cd backend && uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev
```

### Demo Flow (2-4 minutes)

1. **Open Dashboard** → Show SYSTEM ONLINE, explain the SOC console layout
2. **Genuine Call** → Click button, show low-risk operation
3. **Cloned Call** → Click button, narrate the escalation
4. **Step-Up** → Show security intervention, complete OTP verification
5. **Banking** → Show transaction blocked → verified → approved
6. **API Docs** → Open `/docs`, show REST + WebSocket endpoints
7. **Privacy** → Explain no raw audio storage policy
8. **Architecture** → Show detection pipeline, fusion engine, model abstraction

### Key Talking Points
- "Real-time, not batch — risk updates every 500ms"
- "Three independent signals, not one classifier"
- "Prevention, not just detection — transactions are blocked"
- "Privacy by design — raw audio never touches disk"
- "Plug-and-play — real models slot in, same pipeline"

---

## License

This project was developed for Smart India Hackathon 2026.
