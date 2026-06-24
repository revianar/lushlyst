from __future__ import annotations

from collections.abc import AsyncGenerator

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from data.models import Base


class Settings(BaseSettings):
    """Centralized application configuration loaded from the project .env file."""

    DATABASE_URL: str = "postgresql+asyncpg://lushlyst_revian:lushlystll_revian@localhost:5433/lushlyst_db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"ssl": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session for FastAPI endpoints.

    The dependency commits successful requests and rolls back failed ones.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Backward-compatible alias for existing tests and scripts."""
    async for session in get_db():
        yield session


async def init_db() -> None:
    """Create all tables defined by SQLAlchemy models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
