"""FastAPI application with card collection CRUD endpoints."""

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .database import get_db
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
    card = await crud.create_card(db, card_in, current_user.id)
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card master not found",
        )
    return card


@app.get("/cards/sync", response_class=ORJSONResponse)
async def sync_cards(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return all card_master_ids owned by the user for lightweight sync."""
    ids = await crud.get_card_ids_for_sync(db, current_user.id)
    return ORJSONResponse(content=ids)


@app.get("/cards/", response_model=list[CardRead])
async def list_cards(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List cards in the authenticated user's collection with pagination."""
    return await crud.get_cards(db, current_user.id, limit=limit, offset=offset)


@app.get("/cards/{card_id}", response_model=CardRead)
async def get_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get details of a specific card in the user's collection."""
    card = await crud.get_card(db, card_id, current_user.id)
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
    card = await crud.update_card(db, card_id, current_user.id, card_in)
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )
    return card


@app.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a card from the user's collection."""
    deleted = await crud.delete_card(db, card_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )
