import asyncio
import os
import sys
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Load environment variables
load_dotenv()

# Get database URL from environment variables or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sql_app.db")

async def add_user_id_to_prompts():
    """
    Add user_id column to prompts table if it doesn't exist.
    This is a one-time migration script.
    """
    # Create async engine
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        # First, check if the table exists
        table_exists = await conn.scalar(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'")
        )
        
        if not table_exists:
            print("Prompts table does not exist. No migration needed.")
            await engine.dispose()
            return
            
        # Get table info using raw SQLite pragma
        result = await conn.execute(
            text("SELECT name FROM pragma_table_info('prompts') WHERE name='user_id'")
        )
        column_exists = bool(result.fetchone())
        
        if not column_exists:
            print("Adding user_id column to prompts table...")
            # Add user_id column as nullable
            await conn.execute(text("ALTER TABLE prompts ADD COLUMN user_id TEXT"))
            print("Added user_id column to prompts table.")
        else:
            print("user_id column already exists in prompts table.")
    
    await engine.dispose()
    print("Migration completed.")

if __name__ == "__main__":
    print("Starting migration to add user_id to prompts table...")
    asyncio.run(add_user_id_to_prompts())
