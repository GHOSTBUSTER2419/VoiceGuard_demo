"""
VoiceGuard — Database Engine

Async SQLAlchemy engine and session factory.
Supports SQLite (local dev) and PostgreSQL (Docker/production).
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# Create async engine based on DATABASE_URL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    # SQLite needs check_same_thread=False
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

# Session factory — use as async context manager
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency: yields an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
