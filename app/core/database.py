from collections.abc import AsyncGenerator
from functools import lru_cache
from urllib.parse import urlparse

from app.core.config import get_settings


class DatabaseConfigurationError(RuntimeError):
    pass


@lru_cache
def get_async_engine():
    settings = get_settings()

    if not settings.database_url:
        raise DatabaseConfigurationError("DEVNEXUS_DATABASE_URL is required.")

    if "your-project-ref" in settings.database_url:
        raise DatabaseConfigurationError(
            "DEVNEXUS_DATABASE_URL still contains the Supabase placeholder host."
        )

    parsed_url = urlparse(settings.database_url)
    if not parsed_url.hostname or not parsed_url.port:
        raise DatabaseConfigurationError(
            "DEVNEXUS_DATABASE_URL must include a valid host and port."
        )

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
    except ImportError as exc:
        raise DatabaseConfigurationError(
            "Install database dependencies with: python -m pip install sqlalchemy asyncpg"
        ) from exc

    return create_async_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory():
    try:
        from sqlalchemy.ext.asyncio import async_sessionmaker
    except ImportError as exc:
        raise DatabaseConfigurationError(
            "Install database dependencies with: python -m pip install sqlalchemy asyncpg"
        ) from exc

    return async_sessionmaker(
        bind=get_async_engine(),
        expire_on_commit=False,
    )


async def get_db_session() -> AsyncGenerator:
    session_factory = get_session_factory()

    async with session_factory() as session:
        yield session
