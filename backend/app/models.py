from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Table, Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

# Import User model to avoid circular imports
# User model will be imported after it's defined

class Base(DeclarativeBase):
    pass

# Association table for many-to-many relationship between prompts and tags
prompt_tags = Table(
    "prompt_tags",
    Base.metadata,
    Column("prompt_id", Integer, ForeignKey("prompts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    like_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="prompts"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=prompt_tags, back_populates="prompts"
    )
    liked_by_users: Mapped[List["User"]] = relationship(
        "User", 
        secondary="user_likes", 
        back_populates="liked_prompts"
    )

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    prompts: Mapped[List["Prompt"]] = relationship(
        "Prompt", back_populates="category", cascade="all, delete-orphan"
    )

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    prompts: Mapped[List[Prompt]] = relationship(
        "Prompt", secondary=prompt_tags, back_populates="tags"
    )

# User and UserLike models are now in a separate file to avoid circular imports
# Import them here to make them available in the module
from app.models.user import User, UserLike  # noqa: E402
