import json
import os
import sys
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Prompt, Category, Tag, prompt_tags
from app.database import get_db, SQLALCHEMY_DATABASE_URL
from app.main import app

# Load environment variables
load_dotenv()

# Get the absolute path to the prompts.json file (in the project root)
PROMPTS_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'prompts',
    'prompts.json'
)

async def import_prompts():
    # Read the prompts from the JSON file
    try:
        with open(PROMPTS_JSON_PATH, 'r') as f:
            categories_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {PROMPTS_JSON_PATH}")
        return
    except json.JSONDecodeError:
        print(f"Error: {PROMPTS_JSON_PATH} contains invalid JSON")
        return

    # Create database engine and session
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        # Process each category
        for category_name, category_data in categories_data.items():
            # Create or get category
            result = await session.execute(
                select(Category).where(Category.name == category_name)
            )
            category = result.scalars().first()
            
            if not category:
                category = Category(
                    name=category_name,
                    description=category_data.get('description', '')
                )
                session.add(category)
                await session.commit()
                print(f"Created category: {category_name}")
            
            # Process each prompt in the category
            for prompt_data in category_data.get('prompts', []):
                # Create or get tags
                tag_objs = []
                for tag_name in prompt_data.get('tags', []):
                    result = await session.execute(
                        select(Tag).where(Tag.name == tag_name)
                    )
                    tag = result.scalars().first()
                    
                    if not tag:
                        tag = Tag(name=tag_name)
                        session.add(tag)
                        await session.commit()
                    
                    tag_objs.append(tag)
                
                # Create prompt
                prompt = Prompt(
                    title=prompt_data['name'],
                    content=prompt_data['description'],
                    category_id=category.id,
                    created_at=datetime.utcnow(),
                    tags=tag_objs
                )
                
                session.add(prompt)
                await session.commit()
                print(f"  - Added prompt: {prompt_data['name']}")

        print("\nImport completed successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(import_prompts())
