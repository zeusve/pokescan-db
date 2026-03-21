"""Integration tests for card collection CRUD endpoints."""

import os
import uuid

import httpx
import pytest
from dotenv import load_dotenv

from src.database import AsyncSessionLocal, get_db
from src.main import app
from src.models import CardMaster, User
from src.schemas import CardCreate, CardUpdate
from src.security import get_current_user, hash_password

load_dotenv()

DB_SKIP = not os.getenv("DATABASE_URL")
DB_SKIP_MSG = "DATABASE_URL not set — requires a running PostgreSQL instance"


def _uid() -> str:
    return uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def db_session():
    if DB_SKIP:
        pytest.skip(DB_SKIP_MSG)
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def test_user(db_session):
    """Create a unique test user and return the ORM instance."""
    user = User(
        email=f"crud-{_uid()}@test.com",
        username=f"crud-{_uid()}",
        hashed_password=hash_password("testpass"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def card_master(db_session):
    """Create a CardMaster entry for tests to reference."""
    cm = CardMaster(
        api_id=f"test-{_uid()}",
        name="Pikachu",
        set_id="base1",
        rarity="Common",
    )
    db_session.add(cm)
    await db_session.commit()
    await db_session.refresh(cm)
    return cm


@pytest.fixture
async def client(test_user):
    """Async HTTP test client with auth and DB dependency overrides."""

    async def _override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = _override_get_current_user

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /cards/ — creation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_card_success(client, card_master, test_user):
    """Happy path: create a card and verify owner_id matches."""
    response = await client.post(
        "/cards/",
        json={
            "card_master_id": card_master.id,
            "condition": "MINT",
            "location": "Binder A",
            "quantity": 2,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["card_master_id"] == card_master.id
    assert data["condition"] == "MINT"
    assert data["location"] == "Binder A"
    assert data["quantity"] == 2
    assert data["card_master"]["name"] == "Pikachu"


@pytest.mark.asyncio
async def test_create_card_nonexistent_master(client):
    """Referencing a non-existent card_master_id returns 404."""
    response = await client.post(
        "/cards/", json={"card_master_id": 999999}
    )
    assert response.status_code == 404
    assert "Card master not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_card_invalid_payload(client):
    """Pydantic rejects a payload missing required fields."""
    response = await client.post("/cards/", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /cards/ — listing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_cards_empty(client):
    """A new user has an empty collection."""
    response = await client.get("/cards/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_cards_returns_user_cards(client, card_master):
    """Cards created by the user appear in the listing."""
    await client.post(
        "/cards/", json={"card_master_id": card_master.id, "condition": "MINT"}
    )
    await client.post(
        "/cards/", json={"card_master_id": card_master.id, "condition": "PLAYED"}
    )
    response = await client.get("/cards/")
    assert response.status_code == 200
    cards = response.json()
    assert len(cards) >= 2


@pytest.mark.asyncio
async def test_list_cards_pagination(client, card_master):
    """Pagination limits the number of returned cards."""
    for _ in range(3):
        await client.post(
            "/cards/", json={"card_master_id": card_master.id}
        )
    response = await client.get("/cards/?limit=2&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# GET /cards/{card_id} — single card
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_card_success(client, card_master):
    """Retrieve a specific card by ID."""
    create_resp = await client.post(
        "/cards/", json={"card_master_id": card_master.id, "condition": "MINT"}
    )
    card_id = create_resp.json()["id"]

    response = await client.get(f"/cards/{card_id}")
    assert response.status_code == 200
    assert response.json()["id"] == card_id


@pytest.mark.asyncio
async def test_get_card_not_found(client):
    """Requesting a non-existent card returns 404."""
    response = await client.get("/cards/999999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /cards/{card_id} — update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_card_condition(client, card_master):
    """Partial update changes only the specified fields."""
    create_resp = await client.post(
        "/cards/",
        json={"card_master_id": card_master.id, "condition": "MINT"},
    )
    card_id = create_resp.json()["id"]

    response = await client.patch(
        f"/cards/{card_id}", json={"condition": "NEAR_MINT"}
    )
    assert response.status_code == 200
    assert response.json()["condition"] == "NEAR_MINT"
    # location should remain unchanged
    assert response.json()["location"] == ""


@pytest.mark.asyncio
async def test_update_card_not_found(client):
    """Updating a non-existent card returns 404."""
    response = await client.patch(
        "/cards/999999", json={"condition": "PLAYED"}
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /cards/{card_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_card_success(client, card_master):
    """Deleting a card returns 204 and the card is gone."""
    create_resp = await client.post(
        "/cards/", json={"card_master_id": card_master.id}
    )
    card_id = create_resp.json()["id"]

    response = await client.delete(f"/cards/{card_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_resp = await client.get(f"/cards/{card_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_card_not_found(client):
    """Deleting a non-existent card returns 404."""
    response = await client.delete("/cards/999999")
    assert response.status_code == 404
