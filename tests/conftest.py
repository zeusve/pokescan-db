"""Shared pytest fixtures for the pokescan-db test suite."""

import os
import uuid

import httpx
import pytest
import pytest_asyncio
from dotenv import load_dotenv

from src.database import AsyncSessionLocal
from src.main import app
from src.models import CardMaster, User
from src.security import get_current_user, hash_password

load_dotenv()

DB_SKIP = not os.getenv("DATABASE_URL")
DB_SKIP_MSG = "DATABASE_URL not set — requires a running PostgreSQL instance"


def _uid() -> str:
    return uuid.uuid4().hex[:8]


@pytest.fixture
def test_user_data():
    """Generate unique user credentials for each test run (P2 — no hardcoded values)."""
    uid = _uid()
    return {
        "email": f"test-{uid}@test.com",
        "username": f"test-{uid}",
        "password": "testpassword123",
    }


@pytest_asyncio.fixture
async def db_session():
    """Async DB session — skips if DATABASE_URL is not set."""
    if DB_SKIP:
        pytest.skip(DB_SKIP_MSG)
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a unique test user in the database."""
    user = User(
        email=f"fix-{_uid()}@test.com",
        username=f"fix-{_uid()}",
        hashed_password=hash_password("testpass"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def card_master(db_session):
    """Create a CardMaster entry for tests to reference."""
    cm = CardMaster(
        api_id=f"fix-{_uid()}",
        name="Pikachu",
        set_id="base1",
        rarity="Common",
    )
    db_session.add(cm)
    await db_session.commit()
    await db_session.refresh(cm)
    return cm


@pytest_asyncio.fixture
async def client(test_user):
    """Async HTTP client authenticated as test_user via dependency override."""

    async def _override():
        return test_user

    app.dependency_overrides[get_current_user] = _override
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
