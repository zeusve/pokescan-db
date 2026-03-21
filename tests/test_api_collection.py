"""Integration tests for the /cards/ collection API resource.

Covers the full CRUD lifecycle plus security guarantees:
- Authenticated user can create, list, update, and delete cards
- Unauthenticated requests are rejected (401/403)
- User A cannot access User B's cards (data isolation — P8)
"""

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


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session():
    if DB_SKIP:
        pytest.skip(DB_SKIP_MSG)
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a unique test user."""
    user = User(
        email=f"col-{_uid()}@test.com",
        username=f"col-{_uid()}",
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
        api_id=f"col-{_uid()}",
        name="Charizard",
        set_id="base1",
        rarity="Rare",
    )
    db_session.add(cm)
    await db_session.commit()
    await db_session.refresh(cm)
    return cm


@pytest_asyncio.fixture
async def client(test_user):
    """Async HTTP test client authenticated as test_user."""

    async def _override():
        return test_user

    app.dependency_overrides[get_current_user] = _override
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# CRUD lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_card(client, card_master):
    """Authenticated user can add a valid card to their collection."""
    response = await client.post(
        "/cards/",
        json={
            "card_master_id": card_master.id,
            "condition": "MINT",
            "location": "Binder A",
            "quantity": 3,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["card_master_id"] == card_master.id
    assert data["condition"] == "MINT"
    assert data["location"] == "Binder A"
    assert data["quantity"] == 3
    # Response includes nested card master details
    assert data["card_master"] is not None
    assert data["card_master"]["name"] == "Charizard"
    assert data["card_master"]["rarity"] == "Rare"


@pytest.mark.asyncio
async def test_list_cards(client, card_master):
    """Listing returns the authenticated user's cards with card_master info."""
    await client.post(
        "/cards/",
        json={"card_master_id": card_master.id, "condition": "MINT"},
    )
    await client.post(
        "/cards/",
        json={"card_master_id": card_master.id, "condition": "PLAYED"},
    )

    response = await client.get("/cards/")
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) >= 2
    for card in cards:
        assert card["card_master"] is not None
        assert card["card_master"]["name"] == "Charizard"


@pytest.mark.asyncio
async def test_update_card(client, card_master):
    """Partial update modifies only the specified fields (exclude_unset)."""
    create_resp = await client.post(
        "/cards/",
        json={
            "card_master_id": card_master.id,
            "condition": "MINT",
            "location": "Binder A",
            "quantity": 1,
        },
    )
    card_id = create_resp.json()["id"]

    response = await client.patch(
        f"/cards/{card_id}",
        json={"quantity": 5, "location": "Box 3"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 5
    assert data["location"] == "Box 3"
    assert data["condition"] == "MINT"  # unchanged


@pytest.mark.asyncio
async def test_delete_card(client, card_master):
    """After deletion the card is no longer accessible."""
    create_resp = await client.post(
        "/cards/", json={"card_master_id": card_master.id}
    )
    card_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/cards/{card_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/cards/{card_id}")
    assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# Security: unauthenticated access
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Requests without a valid token are rejected on all card endpoints."""
    app.dependency_overrides.clear()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as anon:
        for method, url in [
            ("GET", "/cards/"),
            ("POST", "/cards/"),
            ("GET", "/cards/1"),
            ("PATCH", "/cards/1"),
            ("DELETE", "/cards/1"),
        ]:
            resp = await anon.request(method, url)
            assert resp.status_code in (401, 403), (
                f"{method} {url} returned {resp.status_code}, expected 401 or 403"
            )


# ---------------------------------------------------------------------------
# Security: cross-user data isolation (P8)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_access_other_user_card(db_session, card_master):
    """User B cannot view, update, or delete User A's cards."""
    user_a = User(
        email=f"iso-a-{_uid()}@test.com",
        username=f"iso-a-{_uid()}",
        hashed_password=hash_password("testpass"),
    )
    user_b = User(
        email=f"iso-b-{_uid()}@test.com",
        username=f"iso-b-{_uid()}",
        hashed_password=hash_password("testpass"),
    )
    db_session.add_all([user_a, user_b])
    await db_session.commit()
    await db_session.refresh(user_a)
    await db_session.refresh(user_b)

    async def _as_user_a():
        return user_a

    app.dependency_overrides[get_current_user] = _as_user_a

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # User A creates a card
        create_resp = await client.post(
            "/cards/",
            json={"card_master_id": card_master.id, "condition": "MINT"},
        )
        assert create_resp.status_code == 201
        card_id = create_resp.json()["id"]

        # Switch authentication to user B
        async def _as_user_b():
            return user_b

        app.dependency_overrides[get_current_user] = _as_user_b

        # User B cannot view user A's card
        assert (await client.get(f"/cards/{card_id}")).status_code == 404

        # User B cannot update user A's card
        assert (
            await client.patch(
                f"/cards/{card_id}", json={"condition": "PLAYED"}
            )
        ).status_code == 404

        # User B cannot delete user A's card
        assert (await client.delete(f"/cards/{card_id}")).status_code == 404

        # User B's listing does not include user A's card
        list_resp = await client.get("/cards/")
        assert list_resp.status_code == 200
        assert card_id not in [c["id"] for c in list_resp.json()]

    app.dependency_overrides.clear()
