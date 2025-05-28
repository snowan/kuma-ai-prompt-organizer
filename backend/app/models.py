from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import ForeignKey, Table, Column, Integer, String, DateTime, func, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, object_session

class Base(DeclarativeBase):
    pass

# Association table for many-to-many relationship between prompts and tags
prompt_tags = Table(
    "prompt_tags",
    Base.metadata,
    Column("prompt_id", Integer, ForeignKey("prompts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class PromptLike(Base):
    __tablename__ = "prompt_likes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prompt_id: Mapped[int] = mapped_column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)  # In a real app, this would be a foreign key to a users table
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="likes")
    
    __table_args__ = (
        # Ensure a user can only like a prompt once
        {'sqlite_autoincrement': True},
    )
    __table_args__ = (
        # Composite unique constraint
        {'sqlite_autoincrement': True},
    )

class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)  # Denormalized count for performance
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # ID of the user who created the prompt

    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="prompts"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=prompt_tags, back_populates="prompts"
    )
    likes: Mapped[List["PromptLike"]] = relationship(
        "PromptLike", back_populates="prompt", cascade="all, delete-orphan"
    )
    
    @property
    def likes_count(self) -> int:
        """Return the number of likes for this prompt."""
        return self.like_count
    
    def is_liked_by(self, user_id: str) -> bool:
        """Check if this prompt is liked by a specific user."""
        if not user_id:
            return False
        return any(like.user_id == user_id for like in self.likes)

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
    prompts: Mapped[List["Prompt"]] = relationship(
        "Prompt", secondary=prompt_tags, back_populates="tags"
    )
