"""SQLAlchemy ORM models for pokescan-db entities."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from .constants import VECTOR_DIM
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

    cards: Mapped[list["UserCard"]] = relationship(back_populates="user")


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
    image_hash: Mapped[list[float] | None] = mapped_column(
        Vector(VECTOR_DIM), nullable=True
    )
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    owners: Mapped[list["UserCard"]] = relationship(back_populates="card_master")


class UserCard(Base):
    """Association model representing a user's ownership of a specific card."""

    __tablename__ = "user_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    card_master_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards_master.id", ondelete="CASCADE"), nullable=False, index=True
    )
    condition: Mapped[str] = mapped_column(String, nullable=False, default="UNKNOWN")
    location: Mapped[str] = mapped_column(String, nullable=False, default="")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="cards")
    card_master: Mapped["CardMaster"] = relationship(back_populates="owners")
