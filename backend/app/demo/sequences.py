"""
VoiceGuard — Demo Simulation Sequences

Deterministic, predefined time-series data for SIH demonstration.
These sequences travel through the SAME fusion, smoothing, WebSocket,
alerting, and frontend pipeline as real audio analysis would.

DO NOT generate random numbers. These are reproducible demo sequences
designed to clearly demonstrate the product's capabilities.

Two primary sequences:
    1. GENUINE — natural call, scores stay low
    2. CLONED  — voice cloning attack, scores escalate to critical
"""


def genuine_sequence() -> list[dict]:
    """
    Simulate a genuine caller.

    Characteristics:
    - Spectral: low, stable (natural audio)
    - Prosody: low, naturally varying
    - Speaker: high match (low risk score)
    - Duration: ~15 seconds (30 windows at 500ms)

    The scores should remain in the NORMAL range throughout.
    """
    return [
        # Opening — caller starts speaking
        {"spectral": 8,  "prosody": 6,  "speaker": 5},
        {"spectral": 10, "prosody": 9,  "speaker": 7},
        {"spectral": 12, "prosody": 11, "speaker": 8},
        {"spectral": 11, "prosody": 13, "speaker": 6},
        {"spectral": 14, "prosody": 10, "speaker": 9},
        # Settled — natural conversation
        {"spectral": 13, "prosody": 12, "speaker": 7},
        {"spectral": 15, "prosody": 14, "speaker": 10},
        {"spectral": 12, "prosody": 11, "speaker": 8},
        {"spectral": 16, "prosody": 15, "speaker": 11},
        {"spectral": 14, "prosody": 13, "speaker": 9},
        # Mid-call — slight natural variation
        {"spectral": 18, "prosody": 16, "speaker": 12},
        {"spectral": 15, "prosody": 14, "speaker": 10},
        {"spectral": 17, "prosody": 18, "speaker": 11},
        {"spectral": 13, "prosody": 12, "speaker": 8},
        {"spectral": 16, "prosody": 15, "speaker": 10},
        # Continues stable
        {"spectral": 14, "prosody": 13, "speaker": 9},
        {"spectral": 15, "prosody": 11, "speaker": 7},
        {"spectral": 12, "prosody": 14, "speaker": 8},
        {"spectral": 16, "prosody": 12, "speaker": 10},
        {"spectral": 13, "prosody": 15, "speaker": 9},
        # Closing — natural wind down
        {"spectral": 11, "prosody": 10, "speaker": 7},
        {"spectral": 14, "prosody": 12, "speaker": 8},
        {"spectral": 12, "prosody": 11, "speaker": 6},
        {"spectral": 10, "prosody": 9,  "speaker": 5},
        {"spectral": 9,  "prosody": 8,  "speaker": 5},
        # Final
        {"spectral": 8,  "prosody": 7,  "speaker": 4},
        {"spectral": 7,  "prosody": 6,  "speaker": 4},
        {"spectral": 8,  "prosody": 7,  "speaker": 5},
        {"spectral": 6,  "prosody": 5,  "speaker": 3},
        {"spectral": 5,  "prosody": 4,  "speaker": 3},
    ]


def cloned_sequence() -> list[dict]:
    """
    Simulate a voice cloning / impersonation attack.

    Characteristics:
    - Spectral: starts low, escalates as synthetic artifacts accumulate
    - Prosody: starts low, escalates as flatness/timing issues emerge
    - Speaker: starts with moderate match, degrades as voiceprint diverges
    - Duration: ~20 seconds (40 windows at 500ms)

    The scores should transition: NORMAL → ELEVATED → CRITICAL
    Step-up verification should trigger around window 24-28.
    """
    return [
        # Phase 1: Initial — attacker sounds plausible
        {"spectral": 15, "prosody": 12, "speaker": 10},
        {"spectral": 18, "prosody": 14, "speaker": 12},
        {"spectral": 20, "prosody": 15, "speaker": 15},
        {"spectral": 22, "prosody": 18, "speaker": 18},
        {"spectral": 25, "prosody": 20, "speaker": 22},
        # Phase 2: Subtle anomalies begin
        {"spectral": 28, "prosody": 23, "speaker": 25},
        {"spectral": 32, "prosody": 26, "speaker": 28},
        {"spectral": 35, "prosody": 28, "speaker": 30},
        {"spectral": 38, "prosody": 32, "speaker": 35},
        {"spectral": 42, "prosody": 35, "speaker": 38},
        # Phase 3: Elevated — multiple signals rising
        {"spectral": 45, "prosody": 38, "speaker": 42},
        {"spectral": 48, "prosody": 42, "speaker": 45},
        {"spectral": 52, "prosody": 45, "speaker": 50},
        {"spectral": 55, "prosody": 48, "speaker": 53},
        {"spectral": 58, "prosody": 52, "speaker": 55},
        # Phase 4: Accelerating — convergence
        {"spectral": 62, "prosody": 55, "speaker": 58},
        {"spectral": 65, "prosody": 58, "speaker": 62},
        {"spectral": 68, "prosody": 62, "speaker": 65},
        {"spectral": 71, "prosody": 65, "speaker": 68},
        {"spectral": 73, "prosody": 67, "speaker": 70},
        # Phase 5: Critical — clear impersonation
        {"spectral": 76, "prosody": 70, "speaker": 73},
        {"spectral": 78, "prosody": 72, "speaker": 75},
        {"spectral": 80, "prosody": 74, "speaker": 78},
        {"spectral": 82, "prosody": 76, "speaker": 80},
        {"spectral": 84, "prosody": 78, "speaker": 82},
        # Phase 6: Sustained high risk
        {"spectral": 85, "prosody": 79, "speaker": 84},
        {"spectral": 86, "prosody": 80, "speaker": 85},
        {"spectral": 87, "prosody": 82, "speaker": 86},
        {"spectral": 88, "prosody": 83, "speaker": 87},
        {"spectral": 89, "prosody": 84, "speaker": 88},
        # Phase 7: Peak
        {"spectral": 90, "prosody": 85, "speaker": 89},
        {"spectral": 91, "prosody": 86, "speaker": 90},
        {"spectral": 90, "prosody": 85, "speaker": 89},
        {"spectral": 92, "prosody": 87, "speaker": 91},
        {"spectral": 91, "prosody": 86, "speaker": 90},
        # Sustained
        {"spectral": 90, "prosody": 85, "speaker": 88},
        {"spectral": 89, "prosody": 84, "speaker": 87},
        {"spectral": 91, "prosody": 86, "speaker": 89},
        {"spectral": 90, "prosody": 85, "speaker": 88},
        {"spectral": 88, "prosody": 83, "speaker": 87},
    ]
