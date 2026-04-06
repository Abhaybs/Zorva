"""Async SQLAlchemy engine and session management."""

from uuid import uuid4

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Supabase transaction pooler (PgBouncer) does not support prepared statement
# caching with asyncpg. Detect pooler URL and adjust connection behavior.
is_supabase_pooler = ".pooler.supabase.com" in settings.database_url

engine_kwargs = {
    "echo": settings.app_debug,
}

if is_supabase_pooler:
    engine_kwargs["connect_args"] = {
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    }
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(
    settings.database_url,
    **engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db():
    """FastAPI dependency that yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
