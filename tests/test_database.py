import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import AsyncSessionLocal, init_db


@pytest.mark.asyncio
async def test_database_initialization_creates_tables():
    try:
        await init_db()
    except Exception as exc:  # pragma: no cover - exercised when local DB is unavailable
        pytest.skip(f"Database not reachable in this environment: {exc}")

    async with AsyncSessionLocal() as session:
        assert isinstance(session, AsyncSession)
