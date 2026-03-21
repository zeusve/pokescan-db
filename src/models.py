"""SQLAlchemy ORM models for pokescan-db entities."""

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from .database import Base


class User(Base):
    """User entity for authentication and collection ownership."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class CardMaster(Base):
    """Card entity storing Pokémon card metadata and perceptual hash vector."""

    __tablename__ = "cards_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    set_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    rarity: Mapped[str | None] = mapped_column(String, nullable=True)
    image_hash = mapped_column(Vector(64), nullable=True)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
