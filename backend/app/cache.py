"""
VoiceGuard — Cache Layer

Redis client with in-memory fallback for local development.
Used for ephemeral session state, EMA scores, and simulation state.

PRIVACY: Raw audio must NEVER be stored in cache.
Only scores, risk states, and session metadata are cached.
All keys have TTL to prevent unbounded growth.
"""

import json
import time
from typing import Optional, Any
from app.config import settings


class InMemoryCache:
    """
    In-memory cache that mimics Redis get/set/delete with TTL support.
    Used when REDIS_URL is not configured (local development).
    """

    def __init__(self):
        self._store: dict[str, tuple[Any, Optional[float]]] = {}

    def _is_expired(self, key: str) -> bool:
        if key not in self._store:
            return True
        _, expires_at = self._store[key]
        if expires_at is not None and time.time() > expires_at:
            del self._store[key]
            return True
        return False

    async def get(self, key: str) -> Optional[str]:
        if self._is_expired(key):
            return None
        value, _ = self._store[key]
        return value

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        expires_at = time.time() + ex if ex else None
        self._store[key] = (value, expires_at)

    async def delete(self, key: str):
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return not self._is_expired(key)

    async def close(self):
        self._store.clear()


class RedisCache:
    """Redis-backed cache for production/Docker deployments."""

    def __init__(self, url: str):
        import redis.asyncio as aioredis
        self._redis = aioredis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        await self._redis.set(key, value, ex=ex)

    async def delete(self, key: str):
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(key))

    async def close(self):
        await self._redis.close()


def create_cache():
    """Factory: create Redis or in-memory cache based on configuration."""
    if settings.redis_url:
        return RedisCache(settings.redis_url)
    return InMemoryCache()


# --- Helper functions for structured session state ---

async def get_session_state(cache, session_id: str) -> Optional[dict]:
    """Retrieve session state from cache."""
    raw = await cache.get(f"session:{session_id}")
    if raw:
        return json.loads(raw)
    return None


async def set_session_state(cache, session_id: str, state: dict):
    """
    Store session state in cache with TTL.

    PRIVACY: This must ONLY contain scores, risk states, and metadata.
    Raw audio must NEVER be included in session state.
    """
    await cache.set(
        f"session:{session_id}",
        json.dumps(state),
        ex=settings.session_ttl_seconds,
    )


async def delete_session_state(cache, session_id: str):
    """Remove session state from cache."""
    await cache.delete(f"session:{session_id}")
