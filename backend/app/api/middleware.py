"""
VoiceGuard — API Key Authentication Middleware

Simple API-key authentication via VOICEGUARD_API_KEY environment variable.
When the key is empty/unset, authentication is disabled (development mode).

Security: API keys are never logged or exposed in responses.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Validates API key from X-API-Key header.

    Development mode: key is empty → all requests pass.
    Production mode: key must match VOICEGUARD_API_KEY.

    Exempt paths: /docs, /openapi.json, /redoc, /health
    """

    EXEMPT_PATHS = {"/docs", "/openapi.json", "/redoc", "/health", "/"}

    async def dispatch(self, request: Request, call_next):
        # Skip auth if not enabled
        if not settings.auth_enabled:
            return await call_next(request)

        # Skip auth for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Skip auth for WebSocket (handled separately)
        if request.url.path.endswith("/stream"):
            return await call_next(request)

        # Validate API key
        api_key = request.headers.get("X-API-Key", "")
        if api_key != settings.voiceguard_api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key. Set X-API-Key header.",
            )

        return await call_next(request)
