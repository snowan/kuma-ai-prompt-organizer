from typing import List, Optional, Dict, Any, Union
from fastapi import HTTPException

from sqlalchemy import select, or_
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from thefuzz import fuzz

from . import models, schemas

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (0-100)"""
    return fuzz.token_sort_ratio(text1.lower(), text2.lower())

async def get_prompts(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[models.Prompt]:
    """Get all prompts with optional search"""
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
    
    if search:
        search = f"%{search}%"
        stmt = stmt.filter(
            or_(
                models.Prompt.title.ilike(search),
                models.Prompt.content.ilike(search)
            )
        )
    
    result = await db.execute(stmt)
    prompts = result.scalars().all()
    
    # Ensure all relationships are loaded
    for prompt in prompts:
        if prompt.category:
            await db.refresh(prompt, ['category'])
        if prompt.tags:
            await db.refresh(prompt, ['tags'])
    
    return prompts

async def get_prompt(db: Session, prompt_id: int) -> Optional[models.Prompt]:
    """Get a single prompt by ID"""
    stmt = (
        select(models.Prompt)
        .options(
            selectinload(models.Prompt.category),
            selectinload(models.Prompt.tags)
        )
        .where(models.Prompt.id == prompt_id)
    )
    result = await db.execute(stmt)
    prompt = result.scalars().first()
    
    if prompt:
        # Ensure all relationships are loaded
        if prompt.category:
            await db.refresh(prompt, ['category'])
        if prompt.tags:
            await db.refresh(prompt, ['tags'])
    
    return prompt

async def create_prompt(db: AsyncSession, prompt: schemas.PromptCreate, user_id: int = 1) -> Union[models.Prompt, Dict[str, Any]]:
    """Create a new prompt with tags"""
    try:
        # Check for similar prompts
        existing_prompts = await get_prompts(db)
        for existing in existing_prompts:
            similarity = calculate_similarity(prompt.content, existing.content)
            if similarity > 90:  # 90% similarity threshold
                return {"similar_prompt_id": existing.id, "similarity": similarity}
        
        # Create prompt
        db_prompt = models.Prompt(
            title=prompt.title,
            content=prompt.content,
            category_id=prompt.category_id,
        )
        
        # Add tags if any
        if prompt.tag_names:
            for tag_name in prompt.tag_names:
                tag = await get_or_create_tag(db, tag_name)
                if tag not in db_prompt.tags:
                    db_prompt.tags.append(tag)
        
        db.add(db_prompt)
        await db.commit()
        
        # Refresh the prompt to get the generated ID
        await db.refresh(db_prompt)
        
        # Create a new query to get the prompt with relationships loaded
        stmt = (
            select(models.Prompt)
            .options(
                selectinload(models.Prompt.category),
                selectinload(models.Prompt.tags)
            )
            .where(models.Prompt.id == db_prompt.id)
        )
        
        result = await db.execute(stmt)
        db_prompt = result.scalar_one()
        
        # Create response with proper serialization
        response_data = {
            "id": db_prompt.id,
            "title": db_prompt.title,
            "content": db_prompt.content,
            "created_at": db_prompt.created_at,
            "updated_at": db_prompt.updated_at,
            "category_id": db_prompt.category_id,
            "category": {
                "id": db_prompt.category.id,
                "name": db_prompt.category.name,
                "description": db_prompt.category.description,
                "created_at": db_prompt.category.created_at
            } if db_prompt.category else None,
            "tags": [{
                "id": tag.id,
                "name": tag.name,
                "created_at": tag.created_at
            } for tag in db_prompt.tags],
            "tag_names": [tag.name for tag in db_prompt.tags]
        }
        
        return response_data
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_prompt(
    db: Session, 
    prompt_id: int, 
    prompt: schemas.PromptUpdate
) -> Union[models.Prompt, Dict[str, Any], None]:
    """Update an existing prompt"""
    db_prompt = await get_prompt(db, prompt_id)
    if not db_prompt:
        return None
    
    # Check for similar prompts (excluding self)
    if prompt.content is not None:
        stmt = select(models.Prompt).where(models.Prompt.id != prompt_id)
        result = await db.execute(stmt)
        existing_prompts = result.scalars().all()
        
        for existing in existing_prompts:
            similarity = calculate_similarity(prompt.content, existing.content)
            if similarity > 90:  # 90% similarity threshold
                return {"similar_prompt_id": existing.id, "similarity": similarity}
    
    # Update fields
    update_data = prompt.model_dump(exclude_unset=True, exclude={"tag_names"})
    for key, value in update_data.items():
        setattr(db_prompt, key, value)
    
    # Update tags if provided
    if prompt.tag_names is not None:
        db_prompt.tags = []
        for tag_name in prompt.tag_names:
            tag = await get_or_create_tag(db, tag_name)
            db_prompt.tags.append(tag)
    
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def delete_prompt(db: Session, prompt_id: int) -> Optional[models.Prompt]:
    """Delete a prompt"""
    db_prompt = await get_prompt(db, prompt_id)
    if not db_prompt:
        return None
    
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

async def delete_tag(db: Session, tag_id: int) -> Optional[models.Tag]:
    """Delete a tag (will remove from prompts but not delete prompts)"""
    db_tag = await get_tag(db, tag_id)
    if not db_tag:
        return None
    
    await db.delete(db_tag)
    await db.commit()
    return db_tag
