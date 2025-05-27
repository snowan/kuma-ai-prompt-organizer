import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db, engine as async_engine
from app import models
from app.models.auth import User, UserLike
from app.models import Prompt, Category, Tag

# Sample data
def get_sample_users() -> List[Dict[str, Any]]:
    return [
        {
            "username": "testuser1",
            "email": "test1@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            "is_active": True
        },
        {
            "username": "testuser2",
            "email": "test2@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            "is_active": True
        },
    ]

def get_sample_categories() -> List[Dict[str, Any]]:
    return [
        {
            "name": "Productivity",
            "description": "Prompts to boost your productivity"
        },
        {
            "name": "Creativity",
            "description": "Prompts to spark your creativity"
        },
    ]

def get_sample_prompts() -> List[Dict[str, Any]]:
    return [
        {
            "title": "Morning Routine",
            "content": "What's your morning routine for maximum productivity?",
            "category_name": "Productivity",
            "tags": ["morning", "routine", "productivity"],
            "like_count": 2
        },
        {
            "title": "Creative Writing",
            "content": "Write a short story about a time traveler who can only travel forward in time.",
            "category_name": "Creativity",
            "tags": ["writing", "story", "creativity"],
            "like_count": 1
        },
    ]

async def init_db():
    # Create all tables
    print("Creating database tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")
    
    # Create a session
    async with async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )() as session:
        try:
            # Check if we already have data
            if await session.get(Category, 1) is not None:
                print("Database already has data. Skipping sample data creation.")
                return
            
            print("Creating sample data...")
            
            # Create sample users
            users = []
            for user_data in get_sample_users():
                user = User(**user_data)
                session.add(user)
                users.append(user)
            await session.commit()
            
            # Create sample categories
            categories = {}
            for cat_data in get_sample_categories():
                category = Category(**cat_data)
                session.add(category)
                categories[category.name] = category
            await session.commit()
            
            # Create sample tags and prompts with likes
            all_tags = {}
            for prompt_data in get_sample_prompts():
                # Get or create tags
                tag_objs = []
                for tag_name in prompt_data.pop('tags', []):
                    if tag_name not in all_tags:
                        tag = Tag(name=tag_name)
                        session.add(tag)
                        all_tags[tag_name] = tag
                    tag_objs.append(all_tags[tag_name])
                
                # Create prompt
                category_name = prompt_data.pop('category_name')
                prompt = Prompt(
                    **prompt_data,
                    category_id=categories[category_name].id,
                    tags=tag_objs
                )
                session.add(prompt)
                await session.flush()  # Get the prompt ID
                
                # Create likes for the prompt
                like_count = min(prompt_data.get('like_count', 0), len(users))
                for i in range(like_count):
                    like = UserLike(
                        user_id=users[i].id,
                        prompt_id=prompt.id
                    )
                    session.add(like)
            
            await session.commit()
            print("Sample data created successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
