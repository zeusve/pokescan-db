"""CRUD operations for the user card collection (SRP: database logic only)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import CardMaster, UserCard
from .schemas import CardCreate, CardUpdate


async def get_card_ids_for_sync(db: AsyncSession, user_id: int) -> list[int]:
    """Return raw card_master_id values for all cards owned by a user."""
    result = await db.execute(
        select(UserCard.card_master_id).where(UserCard.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_cards(
    db: AsyncSession, user_id: int, *, limit: int = 20, offset: int = 0
) -> list[UserCard]:
    """Return paginated cards for a specific user."""
    result = await db.execute(
        select(UserCard)
        .where(UserCard.user_id == user_id)
        .options(selectinload(UserCard.card_master))
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_card(
    db: AsyncSession, card_id: int, user_id: int
) -> UserCard | None:
    """Return a single card owned by the user, or None."""
    result = await db.execute(
        select(UserCard)
        .where(UserCard.id == card_id, UserCard.user_id == user_id)
        .options(selectinload(UserCard.card_master))
    )
    return result.scalar_one_or_none()


async def create_card(
    db: AsyncSession, card_in: CardCreate, user_id: int
) -> UserCard | None:
    """Create a new card in the user's collection.

    Returns None if the referenced CardMaster does not exist.
    """
    result = await db.execute(
        select(CardMaster).where(CardMaster.id == card_in.card_master_id)
    )
    if result.scalar_one_or_none() is None:
        return None

    user_card = UserCard(
        user_id=user_id,
        card_master_id=card_in.card_master_id,
        condition=card_in.condition,
        location=card_in.location,
        quantity=card_in.quantity,
    )
    db.add(user_card)
    await db.commit()
    await db.refresh(user_card)

    result = await db.execute(
        select(UserCard)
        .where(UserCard.id == user_card.id)
        .options(selectinload(UserCard.card_master))
    )
    return result.scalar_one()


async def update_card(
    db: AsyncSession, card_id: int, user_id: int, card_in: CardUpdate
) -> UserCard | None:
    """Update a card's metadata. Returns None if not found or not owned."""
    result = await db.execute(
        select(UserCard).where(
            UserCard.id == card_id, UserCard.user_id == user_id
        )
    )
    card = result.scalar_one_or_none()
    if card is None:
        return None

    for field, value in card_in.model_dump(exclude_unset=True).items():
        setattr(card, field, value)

    await db.commit()
    await db.refresh(card)

    result = await db.execute(
        select(UserCard)
        .where(UserCard.id == card.id)
        .options(selectinload(UserCard.card_master))
    )
    return result.scalar_one()


async def delete_card(
    db: AsyncSession, card_id: int, user_id: int
) -> bool:
    """Delete a card from the user's collection. Returns False if not found."""
    result = await db.execute(
        select(UserCard).where(
            UserCard.id == card_id, UserCard.user_id == user_id
        )
    )
    card = result.scalar_one_or_none()
    if card is None:
        return False

    await db.delete(card)
    await db.commit()
    return True
