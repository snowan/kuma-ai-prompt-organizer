import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator, List, Type
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base

# Define the Base class here to avoid circular imports
Base = declarative_base()

# Import models after Base is defined to ensure proper registration
# The models will be imported in models/__init__.py

load_dotenv()

# SQLite database URL - use aiosqlite for async support
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sql_app.db")

# Create async SQLAlchemy engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Enable SQL query logging
)

# Async session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def create_tables(engine: AsyncEngine) -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables(engine: AsyncEngine) -> None:
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Dependency to get DB session
async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependency to get async DB session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
