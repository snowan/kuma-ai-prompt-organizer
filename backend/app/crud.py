from typing import List, Optional, Dict, Any, Union
from fastapi import HTTPException

from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from thefuzz import fuzz

from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Set
from fastapi import HTTPException, status
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from thefuzz import fuzz

from . import models, schemas

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (0-100)"""
    return fuzz.token_sort_ratio(text1.lower(), text2.lower())

async def get_prompts(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    user_id: Optional[str] = None
) -> List[models.Prompt]:
    """
    Get all prompts with optional search, including category and tags.
    If user_id is provided, will include like status for that user.
    """
    # Base query for prompts
    stmt = (
        select(models.Prompt)
        .options(
            selectinload(models.Prompt.category),
            selectinload(models.Prompt.tags)
        )
        .offset(skip)
        .limit(limit)
        .order_by(models.Prompt.updated_at.desc())
    )
    
    # Apply search filter if provided
    if search:
        search = f"%{search}%"
        stmt = stmt.filter(
            or_(
                models.Prompt.title.ilike(search),
                models.Prompt.content.ilike(search)
            )
        )
    
    # Execute the query
    result = await db.execute(stmt)
    prompts = result.scalars().all()
    
    # If user_id is provided, get the set of liked prompt IDs for this user
    user_liked_prompt_ids = set()
    if user_id:
        user_liked_prompt_ids = await get_user_liked_prompt_ids(db, user_id)
    
    # Process each prompt
    for prompt in prompts:
        # Set is_liked flag if user is authenticated
        if user_id:
            prompt.is_liked = prompt.id in user_liked_prompt_ids
        
        # Ensure category is loaded
        if prompt.category_id and not prompt.category:
            prompt.category = await db.get(models.Category, prompt.category_id)
        
        # Ensure tags are loaded
        if prompt.tags is None:
            prompt.tags = []
        elif not prompt.tags:  # If empty list, try to load
            tag_ids = [tag.id for tag in prompt.tags]
            if tag_ids:
                tag_stmt = select(models.Tag).where(models.Tag.id.in_(tag_ids))
                tag_result = await db.execute(tag_stmt)
                prompt.tags = tag_result.scalars().all()
    
    return prompts

async def get_prompt(
    db: AsyncSession, 
    prompt_id: int, 
    user_id: Optional[str] = None
) -> Optional[models.Prompt]:
    """
    Get a single prompt by ID with category and tags.
    If user_id is provided, will include like status for that user.
    """
    # Base query for the prompt
    stmt = (
        select(models.Prompt)
        .options(
            selectinload(models.Prompt.category),
            selectinload(models.Prompt.tags)
        )
        .where(models.Prompt.id == prompt_id)
    )
    
    # Execute the query
    result = await db.execute(stmt)
    prompt = result.scalars().first()
    
    if prompt:
        # Set is_liked flag if user is authenticated
        if user_id:
            prompt.is_liked = await is_prompt_liked_by_user(db, prompt_id, user_id)
        
        # Ensure category is loaded
        if prompt.category_id and not prompt.category:
            prompt.category = await db.get(models.Category, prompt.category_id)
        
        # Ensure tags are loaded
        if prompt.tags is None:
            prompt.tags = []
        elif not prompt.tags:  # If empty list, try to load
            tag_ids = [tag.id for tag in prompt.tags]
            if tag_ids:
                tag_stmt = select(models.Tag).where(models.Tag.id.in_(tag_ids))
                tag_result = await db.execute(tag_stmt)
                prompt.tags = tag_result.scalars().all()
    
    return prompt

async def create_prompt(
    db: AsyncSession, 
    prompt: schemas.PromptCreate, 
    user_id: Optional[str] = None
):
    """
    Create a new prompt with optional category and tags.
    Returns the created prompt or a dictionary with similar prompt info if a similar prompt exists.
    """
    # Check if a similar prompt already exists
    existing_prompts = await get_prompts(db, search=prompt.content, limit=5, user_id=user_id)
    
    for existing_prompt in existing_prompts:
        similarity = calculate_similarity(prompt.content, existing_prompt.content)
        if similarity > 80:  # Threshold for considering prompts similar
            return {
                "similar_prompt_id": existing_prompt.id,
                "similarity": similarity
            }
    
    # Create the prompt
    db_prompt = models.Prompt(
        title=prompt.title,
        content=prompt.content,
        category_id=prompt.category_id,
        user_id=user_id  # Store the user ID who created the prompt
    )
    
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    
    # Add tags if provided
    if prompt.tag_names:
        for tag_name in prompt.tag_names:
            db_tag = await get_or_create_tag(db, tag_name.strip())
            if db_tag not in db_prompt.tags:
                db_prompt.tags.append(db_tag)
        
        await db.commit()
        await db.refresh(db_prompt)
    
    return db_prompt

async def update_prompt(
    db: Session, 
    prompt_id: int, 
    prompt: schemas.PromptUpdate,
    user_id: Optional[str] = None
):
    """
    Update an existing prompt.
    Returns the updated prompt or a dictionary with similar prompt info if a similar prompt exists.
    """
    # Get the existing prompt
    db_prompt = await get_prompt(db, prompt_id, user_id=user_id)
    if not db_prompt:
        return None
    
    # Check if content is being updated and if a similar prompt exists
    if prompt.content and prompt.content != db_prompt.content:
        existing_prompts = await get_prompts(db, search=prompt.content, limit=5, user_id=user_id)
        
        for existing_prompt in existing_prompts:
            if existing_prompt.id == prompt_id:
                continue  # Skip the current prompt
                
            similarity = calculate_similarity(prompt.content, existing_prompt.content)
            if similarity > 80:  # Threshold for considering prompts similar
                return {
                    "similar_prompt_id": existing_prompt.id,
                    "similarity": similarity
                }
    
    # Update prompt fields if provided
    if prompt.title is not None:
        db_prompt.title = prompt.title
    if prompt.content is not None:
        db_prompt.content = prompt.content
    if prompt.category_id is not None:
        db_prompt.category_id = prompt.category_id
    
    # Update tags if provided
    if prompt.tag_names is not None:
        # Clear existing tags
        db_prompt.tags = []
        await db.commit()
        
        # Add new tags
        for tag_name in prompt.tag_names:
            db_tag = await get_or_create_tag(db, tag_name.strip())
            if db_tag not in db_prompt.tags:
                db_prompt.tags.append(db_tag)
    
    db_prompt.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_prompt)
    
    # Return the updated prompt with fresh data
    return await get_prompt(db, prompt_id, user_id=user_id)

async def delete_prompt(
    db: Session, 
    prompt_id: int,
    user_id: Optional[str] = None
):
    """
    Delete a prompt.
    If user_id is provided, only the owner can delete the prompt.
    """
    db_prompt = await get_prompt(db, prompt_id=prompt_id, user_id=user_id)
    if not db_prompt:
        return None
    
    # Check if the user is the owner of the prompt
    if user_id and db_prompt.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this prompt"
        )
    
    await db.delete(db_prompt)
    await db.commit()
    return db_prompt

async def get_or_create_tag(db: AsyncSession, name: str) -> models.Tag:
    """Get or create a tag by name"""
    try:
        # Check if tag exists
        stmt = select(models.Tag).where(models.Tag.name == name)
        result = await db.execute(stmt)
        tag = result.scalar_one_or_none()
        
        if tag is None:
            # Create new tag
            tag = models.Tag(name=name)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        
        return tag
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get or create tag: {str(e)}"
        )

async def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    """Get all categories"""
    stmt = (
        select(models.Category)
        .options(selectinload(models.Category.prompts))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    """Get a category by name"""
    stmt = select(models.Category).where(models.Category.name == name)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    """Get a single category by ID"""
    stmt = (
        select(models.Category)
        .options(selectinload(models.Category.prompts))
        .where(models.Category.id == category_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category"""
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def update_category(
    db: Session, 
    category_id: int, 
    category: schemas.CategoryUpdate
) -> Optional[models.Category]:
    """Update a category"""
    db_category = await get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def delete_category(db: Session, category_id: int) -> Optional[models.Category]:
    """Delete a category"""
    db_category = await get_category(db, category_id)
    if not db_category:
        return None
    
    await db.delete(db_category)
    await db.commit()
    return db_category

async def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tag]:
    """Get all tags"""
    stmt = (
        select(models.Tag)
        .options(selectinload(models.Tag.prompts))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_tag(db: Session, tag_id: int) -> Optional[models.Tag]:
    """Get a single tag by ID"""
    stmt = (
        select(models.Tag)
        .options(selectinload(models.Tag.prompts))
        .where(models.Tag.id == tag_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def delete_tag(db: Session, tag_id: int):
    """Delete a tag (will remove from prompts but not delete prompts)"""
    db_tag = db.get(models.Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(db_tag)
    db.commit()
    return db_tag


async def like_prompt(db: AsyncSession, prompt_id: int, user_id: str) -> models.Prompt:
    """
    Like a prompt for a user. If already liked, removes the like.
    Returns the updated prompt with the new like count.
    """
    # Check if prompt exists
    stmt = select(models.Prompt).where(models.Prompt.id == prompt_id)
    result = await db.execute(stmt)
    prompt = result.scalars().first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Check if already liked
    stmt = select(models.PromptLike).where(
        and_(
            models.PromptLike.prompt_id == prompt_id,
            models.PromptLike.user_id == user_id
        )
    )
    result = await db.execute(stmt)
    existing_like = result.scalars().first()
    
    if existing_like:
        # Unlike: remove the like and decrement count
        await db.delete(existing_like)
        prompt.like_count = max(0, prompt.like_count - 1)
    else:
        # Like: add a new like and increment count
        like = models.PromptLike(prompt_id=prompt_id, user_id=user_id)
        db.add(like)
        prompt.like_count += 1
    
    prompt.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(prompt)
    return prompt


async def get_user_liked_prompt_ids(db: AsyncSession, user_id: str) -> Set[int]:
    """Get a set of prompt IDs that the user has liked"""
    stmt = select(models.PromptLike.prompt_id).where(
        models.PromptLike.user_id == user_id
    )
    result = await db.execute(stmt)
    return {row[0] for row in result.all()}


async def get_prompt_likes_count(db: AsyncSession, prompt_id: int) -> int:
    """Get the number of likes for a prompt"""
    stmt = select(models.Prompt).where(models.Prompt.id == prompt_id)
    result = await db.execute(stmt)
    prompt = result.scalars().first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt.like_count


async def is_prompt_liked_by_user(
    db: AsyncSession, prompt_id: int, user_id: str
) -> bool:
    """Check if a prompt is liked by a specific user"""
    stmt = select(models.PromptLike).where(
        and_(
            models.PromptLike.prompt_id == prompt_id,
            models.PromptLike.user_id == user_id
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first() is not None
