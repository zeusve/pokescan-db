"""Tests for async SQLAlchemy database setup."""

import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()


@pytest.mark.asyncio
async def test_async_connection():
    """Verify that the async engine can connect and execute a simple query."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set — requires a running PostgreSQL instance")
    from src.database import engine

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_async_session_factory():
    """Verify that AsyncSessionLocal produces a valid AsyncSession."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set — requires a running PostgreSQL instance")
    from src.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
