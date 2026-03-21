"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Card collection schemas ---


class CardCreate(BaseModel):
    """Schema for adding a card to the user's collection."""

    card_master_id: int
    condition: str = "UNKNOWN"
    location: str = ""
    quantity: int = 1


class CardUpdate(BaseModel):
    """Schema for partially updating a card in the user's collection."""

    condition: Optional[str] = None
    location: Optional[str] = None
    quantity: Optional[int] = None


class CardMasterRead(BaseModel):
    """Nested read schema for card master details."""

    id: int
    api_id: str
    name: str
    set_id: str
    rarity: Optional[str] = None

    model_config = {"from_attributes": True}


class CardRead(BaseModel):
    """Response schema for a user's collection card."""

    id: int
    card_master_id: int
    condition: str
    location: str
    quantity: int
    created_at: datetime
    card_master: Optional[CardMasterRead] = None

    model_config = {"from_attributes": True}
