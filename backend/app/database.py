import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.models import Base

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

# Dependency to get DB session
async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependency to get async DB session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
