import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import SQLALCHEMY_DATABASE_URL
from app.models import Base, Prompt, PromptLike

# Create a sync engine for operations that don't support async
SYNC_DB_URL = SQLALCHEMY_DATABASE_URL.replace("+aiosqlite", "")
sync_engine = create_engine(SYNC_DB_URL)

async def migrate_likes():
    # Create all tables using the async engine
    async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Use sync connection for operations that don't support async well
    with sync_engine.connect() as conn:
        # Check if the likes column exists in the prompts table
        result = conn.execute(
            text("""
            SELECT COUNT(*) FROM pragma_table_info('prompts') 
            WHERE name = 'likes';
            """)
        )
        
        if result.scalar() > 0:
            # Rename the column
            conn.execute(
                text("ALTER TABLE prompts RENAME COLUMN likes TO like_count;")
            )
            print("✅ Renamed 'likes' column to 'like_count'")
        
        # Create a unique index on prompt_id and user_id if it doesn't exist
        conn.execute(
            text("""
            CREATE TABLE IF NOT EXISTS prompt_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id INTEGER NOT NULL,
                user_id VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_id) REFERENCES prompts (id) ON DELETE CASCADE,
                UNIQUE (prompt_id, user_id)
            );
            """)
        )
        
        # Create index
        conn.execute(
            text("""
            CREATE INDEX IF NOT EXISTS ix_prompt_likes_prompt_user 
            ON prompt_likes (prompt_id, user_id);
            """)
        )
        
        # Commit the changes
        conn.commit()
    
    print("✅ Migration completed successfully!")

if __name__ == "__main__":
    print("Starting database migration...")
    asyncio.run(migrate_likes())
