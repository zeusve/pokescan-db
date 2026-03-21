"""FastAPI application with card collection CRUD endpoints."""

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .database import get_db
from .models import CardMaster, UserCard
from .schemas import CardCreate, CardRead, CardUpdate
from .security import get_current_user

app = FastAPI(title="PokeScan DB", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/cards/", response_model=CardRead, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_in: CardCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add a card to the authenticated user's collection."""
    result = await db.execute(
        select(CardMaster).where(CardMaster.id == card_in.card_master_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card master not found",
        )

    user_card = UserCard(
        user_id=current_user.id,
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


@app.get("/cards/", response_model=list[CardRead])
async def list_cards(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List cards in the authenticated user's collection with pagination."""
    result = await db.execute(
        select(UserCard)
        .where(UserCard.user_id == current_user.id)
        .options(selectinload(UserCard.card_master))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@app.get("/cards/{card_id}", response_model=CardRead)
async def get_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get details of a specific card in the user's collection."""
    result = await db.execute(
        select(UserCard)
        .where(UserCard.id == card_id, UserCard.user_id == current_user.id)
        .options(selectinload(UserCard.card_master))
    )
    card = result.scalar_one_or_none()
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )
    return card


@app.patch("/cards/{card_id}", response_model=CardRead)
async def update_card(
    card_id: int,
    card_in: CardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a card's metadata in the user's collection."""
    result = await db.execute(
        select(UserCard).where(
            UserCard.id == card_id, UserCard.user_id == current_user.id
        )
    )
    card = result.scalar_one_or_none()
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )

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


@app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a card from the user's collection."""
    result = await db.execute(
        select(UserCard).where(
            UserCard.id == card_id, UserCard.user_id == current_user.id
        )
    )
    card = result.scalar_one_or_none()
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )

    await db.delete(card)
    await db.commit()
