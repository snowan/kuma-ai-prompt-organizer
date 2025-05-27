import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine, Base
from app.models import Prompt, PromptLike

async def migrate_likes():
    # Create all tables
    async with engine.begin() as conn:
        # Create the prompt_likes table
        await conn.run_sync(Base.metadata.create_all)
        
        # Rename the existing likes column to like_count if it exists
        try:
            # SQLite specific way to check if column exists
            result = await conn.execute(
                text("""
                SELECT COUNT(*) FROM pragma_table_info('prompts') 
                WHERE name = 'likes';
                """)
            )
            if result.scalar() > 0:
                # Rename the column
                await conn.execute(
                    text("ALTER TABLE prompts RENAME COLUMN likes TO like_count;")
                )
                print("Renamed 'likes' column to 'like_count'")
        except Exception as e:
            print(f"Error renaming column: {e}")
            
        # Create a unique index on prompt_id and user_id
        try:
            await conn.execute(
                text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_prompt_likes_prompt_user 
                ON prompt_likes (prompt_id, user_id);
                """)
            )
            print("Created unique index on prompt_likes(prompt_id, user_id)")
        except Exception as e:
            print(f"Error creating index: {e}")
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate_likes())
