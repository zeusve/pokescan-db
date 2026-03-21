"""Tests for SQLAlchemy ORM models (User, CardMaster)."""

import os
import uuid

import pytest
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.models import CardMaster
from src.vision import ImageHasher

load_dotenv()

DB_SKIP_MSG = "DATABASE_URL not set — requires a running PostgreSQL instance"


def _random_email() -> str:
    """Generate a unique email to avoid collisions between test runs."""
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def _random_username() -> str:
    """Generate a unique username to avoid collisions between test runs."""
    return f"user-{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_create_user():
    """Verify that a User can be persisted and retrieved."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip(DB_SKIP_MSG)
    from src.database import AsyncSessionLocal
    from src.models import User

    email = _random_email()
    username = _random_username()
    async with AsyncSessionLocal() as session:
        user = User(email=email, username=username, hashed_password="hashed_abc123")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        assert user.id is not None
        assert user.email == email
        assert user.username == username


@pytest.mark.asyncio
async def test_user_email_uniqueness():
    """Verify that duplicate emails raise IntegrityError."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip(DB_SKIP_MSG)
    from src.database import AsyncSessionLocal
    from src.models import User

    email = _random_email()
    async with AsyncSessionLocal() as session:
        session.add(User(email=email, username=_random_username(), hashed_password="hash1"))
        await session.commit()

    async with AsyncSessionLocal() as session:
        session.add(User(email=email, username=_random_username(), hashed_password="hash2"))
        with pytest.raises(IntegrityError):
            await session.commit()


@pytest.mark.asyncio
async def test_user_username_uniqueness():
    """Verify that duplicate usernames raise IntegrityError."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip(DB_SKIP_MSG)
    from src.database import AsyncSessionLocal
    from src.models import User

    username = _random_username()
    async with AsyncSessionLocal() as session:
        session.add(User(email=_random_email(), username=username, hashed_password="hash1"))
        await session.commit()

    async with AsyncSessionLocal() as session:
        session.add(User(email=_random_email(), username=username, hashed_password="hash2"))
        with pytest.raises(IntegrityError):
            await session.commit()


@pytest.mark.asyncio
async def test_user_default_values():
    """Verify is_active defaults to True and created_at is auto-generated."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip(DB_SKIP_MSG)
    from src.database import AsyncSessionLocal
    from src.models import User

    email = _random_email()
    async with AsyncSessionLocal() as session:
        user = User(email=email, username=_random_username(), hashed_password="hash_default")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        assert user.is_active is True
        assert user.created_at is not None


def _random_api_id() -> str:
    """Generate a unique API ID to avoid collisions between test runs."""
    return f"test-{uuid.uuid4().hex[:12]}"


@pytest.mark.asyncio
async def test_create_card_master():
    """Verify that a CardMaster with a VECTOR_DIM-dim vector can be persisted and retrieved."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip(DB_SKIP_MSG)
    from src.database import AsyncSessionLocal

    api_id = _random_api_id()
    test_vector = [0.1] * ImageHasher.VECTOR_DIM

    async with AsyncSessionLocal() as session:
        card = CardMaster(
            api_id=api_id,
            name="Pikachu VMAX",
            set_id="swsh4",
            rarity="Rare Holo VMAX",
            image_hash=test_vector,
        )
        session.add(card)
        await session.commit()
        await session.refresh(card)

        assert card.id is not None
        assert card.api_id == api_id
        assert card.name == "Pikachu VMAX"
        assert card.set_id == "swsh4"
        assert card.created_at is not None

    # Re-fetch to verify vector integrity
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CardMaster).where(CardMaster.api_id == api_id)
        )
        fetched = result.scalar_one()
        assert len(fetched.image_hash) == ImageHasher.VECTOR_DIM
        assert abs(fetched.image_hash[0] - 0.1) < 1e-6


@pytest.mark.asyncio
async def test_card_api_id_uniqueness():
    """Verify that duplicate api_id raises IntegrityError."""
    if not os.getenv("DATABASE_URL"):
        pytest.skip(DB_SKIP_MSG)
    from src.database import AsyncSessionLocal

    api_id = _random_api_id()
    async with AsyncSessionLocal() as session:
        session.add(CardMaster(api_id=api_id, name="Card A", set_id="set1"))
        await session.commit()

    async with AsyncSessionLocal() as session:
        session.add(CardMaster(api_id=api_id, name="Card B", set_id="set2"))
        with pytest.raises(IntegrityError):
            await session.commit()


def test_card_master_vector_dimension():
    """Verify that CardMaster vector dimension matches ImageHasher config (P2)."""
    column_type = CardMaster.__table__.columns.image_hash.type
    assert column_type.dim == ImageHasher.VECTOR_DIM


def test_card_master_instantiation_with_vector():
    """Verify CardMaster can be instantiated with a VECTOR_DIM-sized vector."""
    vector = [float(i) / ImageHasher.VECTOR_DIM for i in range(ImageHasher.VECTOR_DIM)]
    card = CardMaster(
        api_id="test-instantiation",
        name="Test Card",
        set_id="test-set",
        image_hash=vector,
    )
    assert card.image_hash is not None
    assert len(card.image_hash) == ImageHasher.VECTOR_DIM
