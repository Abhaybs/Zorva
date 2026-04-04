"""Database initialisation helpers."""

from app.db.database import engine, Base


async def init_database():
    """Create all tables — use only in development."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_database():
    """Drop all tables — use only in development."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
