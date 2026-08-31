"""
VoiceGuard — Database Initialization

Creates tables and seeds default organization configuration.
"""

from app.db.engine import engine
from app.db.models import Base, OrgConfig
from app.db.engine import async_session
from app.config import settings
from sqlalchemy import select


async def init_db():
    """Create all tables and seed defaults."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default org config if not exists
    async with async_session() as session:
        result = await session.execute(
            select(OrgConfig).where(OrgConfig.org_id == "default")
        )
        if result.scalar_one_or_none() is None:
            default_config = OrgConfig(
                org_id="default",
                risk_threshold=settings.default_risk_threshold,
                workflow=settings.default_workflow,
                transaction_thresholds={
                    "GENERAL_QUERY": 80,
                    "PAYROLL_CHANGE": 65,
                    "FUND_TRANSFER": 60,
                    "ACCOUNT_CHANGE": 60,
                    "PASSWORD_RESET": 55,
                },
            )
            session.add(default_config)
            await session.commit()
