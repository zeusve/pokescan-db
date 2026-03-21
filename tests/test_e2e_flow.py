"""End-to-end integration tests validating the full user workflow.

These tests use REAL JWT tokens (no dependency overrides) to verify the
complete authentication -> collection management pipeline:

    User created in DB -> JWT token generated -> Add card -> List -> Update -> Delete

Note: /auth/register, /auth/login, and /scan endpoints are not yet implemented.
Once they exist, this suite should be extended to call them directly instead of
creating users and tokens programmatically.
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
from src.security import create_access_token, hash_password

load_dotenv()

DB_SKIP = not os.getenv("DATABASE_URL")
DB_SKIP_MSG = "DATABASE_URL not set — requires a running PostgreSQL instance"


def _uid() -> str:
    return uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------------
# E2E-specific fixtures (no dependency overrides — real JWT auth)
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def e2e_db():
    """Async DB session for E2E test setup."""
    if DB_SKIP:
        pytest.skip(DB_SKIP_MSG)
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def e2e_user(e2e_db):
    """Create a test user and return (user_model, raw_password)."""
    password = "e2e-secure-pass-123"
    user = User(
        email=f"e2e-{_uid()}@test.com",
        username=f"e2e-{_uid()}",
        hashed_password=hash_password(password),
    )
    e2e_db.add(user)
    await e2e_db.commit()
    await e2e_db.refresh(user)
    return user, password


@pytest_asyncio.fixture
async def e2e_card_master(e2e_db):
    """Create a CardMaster entry for E2E tests."""
    cm = CardMaster(
        api_id=f"e2e-{_uid()}",
        name="Pikachu",
        set_id="base1",
        rarity="Common",
    )
    e2e_db.add(cm)
    await e2e_db.commit()
    await e2e_db.refresh(cm)
    return cm


@pytest_asyncio.fixture
async def e2e_client():
    """Unauthenticated async HTTP client — NO dependency overrides."""
    app.dependency_overrides.clear()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


def _auth_headers(user) -> dict:
    """Generate Authorization header with a real JWT for the given user."""
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# E2E: Full user workflow (happy path)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_user_workflow(e2e_client, e2e_user, e2e_card_master):
    """E2E happy path: create user -> get token -> add card -> list -> update -> delete.

    Uses a real JWT token through the full get_current_user dependency chain.
    No dependency overrides — exercises the actual security middleware.
    """
    user, _ = e2e_user
    headers = _auth_headers(user)

    # Step 1: Add card to collection
    create_resp = await e2e_client.post(
        "/cards/",
        json={
            "card_master_id": e2e_card_master.id,
            "condition": "MINT",
            "location": "Binder A",
            "quantity": 2,
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    card_data = create_resp.json()
    assert card_data["card_master_id"] == e2e_card_master.id
    assert card_data["condition"] == "MINT"
    assert card_data["location"] == "Binder A"
    assert card_data["quantity"] == 2
    assert card_data["card_master"]["name"] == "Pikachu"
    card_id = card_data["id"]

    # Step 2: Verify card appears in collection listing
    list_resp = await e2e_client.get("/cards/", headers=headers)
    assert list_resp.status_code == 200
    cards = list_resp.json()
    assert card_id in [c["id"] for c in cards]

    # Step 3: Update the card
    update_resp = await e2e_client.patch(
        f"/cards/{card_id}",
        json={"quantity": 5, "location": "Box 1"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["quantity"] == 5
    assert updated["location"] == "Box 1"
    assert updated["condition"] == "MINT"  # unchanged

    # Step 4: Verify via sync endpoint
    sync_resp = await e2e_client.get("/cards/sync", headers=headers)
    assert sync_resp.status_code == 200
    assert e2e_card_master.id in sync_resp.json()

    # Step 5: Delete the card
    delete_resp = await e2e_client.delete(f"/cards/{card_id}", headers=headers)
    assert delete_resp.status_code == 204

    # Step 6: Verify card is gone
    final_resp = await e2e_client.get("/cards/", headers=headers)
    assert final_resp.status_code == 200
    assert card_id not in [c["id"] for c in final_resp.json()]


# ---------------------------------------------------------------------------
# E2E: Unauthorized collection access
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unauthorized_collection_access(e2e_client):
    """E2E: All card endpoints reject requests without a valid token (401/403)."""
    for method, url in [
        ("GET", "/cards/"),
        ("POST", "/cards/"),
        ("GET", "/cards/1"),
        ("PATCH", "/cards/1"),
        ("DELETE", "/cards/1"),
        ("GET", "/cards/sync"),
    ]:
        resp = await e2e_client.request(method, url)
        assert resp.status_code in (401, 403), (
            f"{method} {url} returned {resp.status_code}, expected 401 or 403"
        )


# ---------------------------------------------------------------------------
# E2E: Invalid/expired token
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_token_rejected(e2e_client):
    """E2E: A tampered or malformed JWT is rejected with 401."""
    headers = {"Authorization": "Bearer invalid.token.here"}
    resp = await e2e_client.get("/cards/", headers=headers)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# E2E: Non-existent card master
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_nonexistent_card_master(e2e_client, e2e_user):
    """E2E: Adding a card referencing a non-existent card_master_id returns 404."""
    user, _ = e2e_user
    headers = _auth_headers(user)

    resp = await e2e_client.post(
        "/cards/",
        json={"card_master_id": 999999, "condition": "MINT"},
        headers=headers,
    )
    assert resp.status_code == 404
