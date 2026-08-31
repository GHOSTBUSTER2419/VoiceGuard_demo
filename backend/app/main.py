"""
VoiceGuard — FastAPI Application Entry Point

AI-Powered Real-Time Voice Cloning & Impersonation Detection
SIH Problem Statement: SIH26104

This is the main application factory. It:
1. Creates the FastAPI app with metadata
2. Configures CORS for frontend access
3. Mounts all API routers
4. Initializes database on startup
5. Applies authentication middleware

Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.init_db import init_db
from app.api.middleware import APIKeyMiddleware

# Import routers
from app.api.sessions import router as sessions_router
from app.api.voiceprints import router as voiceprints_router
from app.api.orgs import router as orgs_router
from app.api.alerts import router as alerts_router
from app.api.demo import router as demo_router
from app.api.ws import router as ws_router
from app.api.banking import router as banking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    await init_db()
    print(f"[VoiceGuard] System online — mode: {settings.model_mode}")
    print(f"[VoiceGuard] Auth: {'enabled' if settings.auth_enabled else 'disabled (development)'}")
    print(f"[VoiceGuard] Database: {settings.database_url.split('://')[0]}")
    print(f"[VoiceGuard] API docs: http://localhost:{settings.api_port}/docs")
    yield
    # Shutdown
    print("[VoiceGuard] Shutting down...")


app = FastAPI(
    title="VoiceGuard API",
    description=(
        "AI-Powered Real-Time Voice Cloning & Impersonation Detection.\n\n"
        "VoiceGuard continuously analyzes incoming speech in streaming windows "
        "and updates an impersonation risk score in real time.\n\n"
        "**Demo mode** uses deterministic simulated model outputs. "
        "**Production mode** is designed for real detection models.\n\n"
        "SIH Problem Statement: SIH26104"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Middleware ---
app.add_middleware(APIKeyMiddleware)

# --- Mount Routers ---
app.include_router(sessions_router)
app.include_router(voiceprints_router)
app.include_router(orgs_router)
app.include_router(alerts_router)
app.include_router(demo_router)
app.include_router(ws_router)
app.include_router(banking_router)


# --- Health Check ---
@app.get("/health", tags=["System"])
async def health():
    """System health check."""
    return {
        "status": "online",
        "service": "VoiceGuard",
        "mode": settings.model_mode,
        "auth_enabled": settings.auth_enabled,
    }


@app.get("/", tags=["System"])
async def root():
    """API root — redirects to docs."""
    return {
        "service": "VoiceGuard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "mode": settings.model_mode,
    }
