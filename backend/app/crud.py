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
) -> List[dict]:
    """
    Get all prompts with optional search, including category and tags.
    If user_id is provided, will include like status for that user.
    Returns a list of prompt dictionaries.
    """
    try:
        # Base query for prompts with category and tags
        stmt = (
            select(models.Prompt)
            .options(
                selectinload(models.Prompt.category),
                selectinload(models.Prompt.tags)
            )
            .offset(skip)
            .limit(limit)
            .order_by(models.Prompt.created_at.desc())
        )
        
        # Apply search filter if provided
        if search:
            stmt = stmt.where(
                or_(
                    models.Prompt.title.ilike(f"%{search}%"),
                    models.Prompt.content.ilike(f"%{search}%")
                )
            )
        
        # Execute the query
        result = await db.execute(stmt)
        prompts = result.scalars().all()
        
        # Get liked prompt IDs for the user if user_id is provided
        user_liked_prompt_ids = set()
        if user_id:
            stmt = select(models.PromptLike.prompt_id).where(
                models.PromptLike.user_id == user_id
            )
            result = await db.execute(stmt)
            user_liked_prompt_ids = {row[0] for row in result.all()}
        
        # Prepare the response
        prompt_list = []
        for prompt in prompts:
            # Prepare category data
            category_data = None
            if prompt.category:
                category_data = {
                    "id": prompt.category.id,
                    "name": prompt.category.name,
                    "description": prompt.category.description,
                    "created_at": prompt.category.created_at
                }
            
            # Prepare tags data
            tags_data = []
            if prompt.tags:
                for tag in prompt.tags:
                    tags_data.append({
                        "id": tag.id,
                        "name": tag.name,
                        "created_at": tag.created_at
                    })
            
            prompt_dict = {
                "id": prompt.id,
                "title": prompt.title,
                "content": prompt.content,
                "category_id": prompt.category_id,
                "created_at": prompt.created_at,
                "updated_at": prompt.updated_at,
                "like_count": prompt.like_count or 0,
                "user_id": prompt.user_id,
                "category": category_data,
                "tags": tags_data,
                "tag_names": [tag.name for tag in (prompt.tags or [])],
                "is_liked": prompt.id in user_liked_prompt_ids
            }
            prompt_list.append(prompt_dict)
        
        return prompt_list
        
    except Exception as e:
        print(f"Error in get_prompts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving prompts: {str(e)}"
        )

async def get_prompt(
    db: AsyncSession, 
    prompt_id: int, 
    user_id: Optional[str] = None
) -> Optional[dict]:
    """
    Get a single prompt by ID with category and tags.
    If user_id is provided, will include like status for that user.
    Returns a dictionary with the prompt data.
    """
    try:
        # Get the prompt with category and tags
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
        
        if not prompt:
            return None
        
        # Check if the prompt is liked by the user
        is_liked = False
        if user_id:
            is_liked = await is_prompt_liked_by_user(db, prompt_id, user_id)
        
        # Get category data
        category_data = None
        if prompt.category:
            category_data = {
                "id": prompt.category.id,
                "name": prompt.category.name,
                "description": prompt.category.description,
                "created_at": prompt.category.created_at
            }
        
        # Get tags data
        tags_data = []
        if hasattr(prompt, 'tags') and prompt.tags:
            tags_data = [
                {
                    "id": tag.id, 
                    "name": tag.name,
                    "created_at": tag.created_at
                } 
                for tag in prompt.tags
            ]
        
        # Create the response dictionary
        response = {
            "id": prompt.id,
            "title": prompt.title,
            "content": prompt.content,
            "category_id": prompt.category_id,
            "user_id": prompt.user_id,
            "like_count": prompt.like_count,
            "created_at": prompt.created_at,
            "updated_at": prompt.updated_at,
            "category": category_data,
            "tags": tags_data,
            "is_liked": is_liked
        }
        
        return response
        
    except Exception as e:
        print(f"Error in get_prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving prompt: {str(e)}"
        )

async def create_prompt(
    db: AsyncSession, 
    prompt: schemas.PromptCreate, 
    user_id: Optional[str] = None
):
    """
    Create a new prompt with optional category and tags.
    Returns the created prompt or a dictionary with similar prompt info if a similar prompt exists.
    """
    try:
        # First, check if category exists
        stmt = select(models.Category).where(models.Category.id == prompt.category_id)
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Create the prompt
        db_prompt = models.Prompt(
            title=prompt.title,
            content=prompt.content,
            category_id=prompt.category_id,
            user_id=user_id,
            like_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(db_prompt)
        await db.flush()  # Get the ID
        
        # Handle tags if provided
        if hasattr(prompt, 'tag_names') and prompt.tag_names:
            tag_objs = []
            for tag_name in prompt.tag_names:
                tag_name = tag_name.strip()
                if not tag_name:
                    continue
                    
                # Check if tag exists
                tag_stmt = select(models.Tag).where(models.Tag.name == tag_name)
                tag_result = await db.execute(tag_stmt)
                tag = tag_result.scalar_one_or_none()
                
                # Create tag if it doesn't exist
                if not tag:
                    tag = models.Tag(name=tag_name, created_at=datetime.utcnow())
                    db.add(tag)
                    await db.flush()
                
                tag_objs.append(tag)
            
            # Create association objects for the many-to-many relationship
            for tag in tag_objs:
                stmt = select(models.prompt_tags).where(
                    models.prompt_tags.c.prompt_id == db_prompt.id,
                    models.prompt_tags.c.tag_id == tag.id
                )
                result = await db.execute(stmt)
                if not result.scalar_one_or_none():
                    stmt = models.prompt_tags.insert().values(
                        prompt_id=db_prompt.id,
                        tag_id=tag.id
                    )
                    await db.execute(stmt)
        
        # Commit the transaction
        await db.commit()
        
        # Build the response
        response = {
            "id": db_prompt.id,
            "title": db_prompt.title,
            "content": db_prompt.content,
            "category_id": db_prompt.category_id,
            "user_id": db_prompt.user_id,
            "like_count": db_prompt.like_count,
            "created_at": db_prompt.created_at,
            "updated_at": db_prompt.updated_at,
            "category": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at
            },
            "tags": [{"id": tag.id, "name": tag.name, "created_at": tag.created_at} for tag in tag_objs],
            "is_liked": False
        }
        
        return response
            
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in create_prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating prompt: {str(e)}"
        )


async def update_prompt(
    db: AsyncSession, 
    prompt_id: int, 
    prompt: schemas.PromptUpdate,
    user_id: Optional[str] = None
):
    """
    Update an existing prompt.
    Returns the updated prompt or a dictionary with similar prompt info if a similar prompt exists.
    """
    try:
        # First get the existing prompt with relationships
        stmt = (
            select(models.Prompt)
            .options(
                selectinload(models.Prompt.category),
                selectinload(models.Prompt.tags)
            )
            .where(models.Prompt.id == prompt_id)
        )
        result = await db.execute(stmt)
        db_prompt = result.scalars().first()
        
        if db_prompt is None:
            raise HTTPException(status_code=404, detail="Prompt not found")
            
        # Check if user is authorized (if user_id is provided, they must be the owner)
        if user_id and db_prompt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this prompt"
            )
            
        # Check for similar prompts if content is being updated
        if prompt.content and prompt.content != db_prompt.content:
            stmt = select(models.Prompt).where(
                and_(
                    or_(
                        models.Prompt.title.ilike(f"%{prompt.content}%"),
                        models.Prompt.content.ilike(f"%{prompt.content}%")
                    ),
                    models.Prompt.id != prompt_id
                )
            ).limit(5)
            
            result = await db.execute(stmt)
            existing_prompts = result.scalars().all()
            
            # Check for similar prompts
            for existing_prompt in existing_prompts:
                similarity = calculate_similarity(prompt.content, existing_prompt.content)
                if similarity > 80:  # Threshold for considering prompts similar
                    return {
                        "similar_prompt_id": existing_prompt.id,
                        "similarity": similarity
                    }
        
        # Update prompt fields
        update_data = prompt.dict(exclude_unset=True)
        
        # Handle tag updates if provided
        if 'tag_names' in update_data:
            tag_names = update_data.pop('tag_names')
            
            # Clear existing tags
            db_prompt.tags = []
            await db.flush()
            
            # Add new tags
            for tag_name in tag_names:
                tag = await get_or_create_tag(db, tag_name.strip())
                if tag not in db_prompt.tags:
                    db_prompt.tags.append(tag)
        
        # Update other fields
        for field, value in update_data.items():
            if hasattr(db_prompt, field):
                setattr(db_prompt, field, value)
        
        db_prompt.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(db_prompt)
        
        # Get the updated prompt with relationships
        updated_prompt = await get_prompt(db, prompt_id=prompt_id, user_id=user_id)
        
        if updated_prompt is None:
            raise HTTPException(status_code=404, detail="Prompt not found after update")
            
        return updated_prompt
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in update_prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating prompt: {str(e)}"
        )

async def delete_prompt(
    db: AsyncSession, 
    prompt_id: int,
    user_id: Optional[str] = None
) -> Optional[dict]:
    """
    Delete a prompt.
    If user_id is provided, only the owner can delete the prompt.
    Returns the deleted prompt data or None if not found.
    """
    try:
        # First get the prompt with relationships to return it later
        stmt = (
            select(models.Prompt)
            .options(
                selectinload(models.Prompt.category),
                selectinload(models.Prompt.tags)
            )
            .where(models.Prompt.id == prompt_id)
        )
        result = await db.execute(stmt)
        db_prompt = result.scalars().first()
        
        if not db_prompt:
            return None
            
        # Check if the user is the owner of the prompt
        if user_id and db_prompt.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this prompt"
            )
        
        # Create a copy of the prompt data to return
        prompt_data = {
            "id": db_prompt.id,
            "title": db_prompt.title,
            "content": db_prompt.content,
            "category_id": db_prompt.category_id,
            "user_id": db_prompt.user_id,
            "created_at": db_prompt.created_at,
            "updated_at": db_prompt.updated_at,
            "like_count": db_prompt.like_count,
            "category": db_prompt.category,
            "tags": db_prompt.tags or [],
            "is_liked": False
        }
        
        # Delete the prompt
        await db.delete(db_prompt)
        await db.commit()
        
        return prompt_data
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in delete_prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting prompt: {str(e)}"
        )

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

async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Category]:
    """Get all categories"""
    stmt = (
        select(models.Category)
        .options(selectinload(models.Category.prompts))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_category_by_name(db: AsyncSession, name: str) -> Optional[models.Category]:
    """Get a category by name"""
    stmt = select(models.Category).where(models.Category.name == name)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_category(db: AsyncSession, category_id: int) -> Optional[models.Category]:
    """Get a single category by ID"""
    stmt = (
        select(models.Category)
        .options(selectinload(models.Category.prompts))
        .where(models.Category.id == category_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_category(db: AsyncSession, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category"""
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def update_category(
    db: AsyncSession, 
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

async def get_tags(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Tag]:
    """Get all tags"""
    stmt = (
        select(models.Tag)
        .options(selectinload(models.Tag.prompts))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_tag(db: AsyncSession, tag_id: int) -> Optional[models.Tag]:
    """Get a single tag by ID"""
    stmt = (
        select(models.Tag)
        .options(selectinload(models.Tag.prompts))
        .where(models.Tag.id == tag_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def delete_tag(db: AsyncSession, tag_id: int):
    """Delete a tag (will remove from prompts but not delete prompts)"""
    db_tag = await db.get(models.Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(db_tag)
    await db.commit()
    return db_tag


async def like_prompt(db: AsyncSession, prompt_id: int, user_id: Optional[str] = None) -> dict:
    """
    Like a prompt for a user. If already liked, removes the like.
    Returns the updated prompt with the new like count in the standard format.
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to like a prompt"
        )
    
    try:
        # Check if prompt exists using get_prompt to ensure consistent data format
        prompt = await get_prompt(db, prompt_id, user_id=user_id)
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
        
        # Get the actual prompt model for updates
        db_prompt = await db.get(models.Prompt, prompt_id)
        if not db_prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        if existing_like:
            # Unlike: remove the like and decrement count
            await db.delete(existing_like)
            db_prompt.like_count = max(0, db_prompt.like_count - 1)
            is_liked = False
        else:
            # Like: add a new like and increment count
            like = models.PromptLike(prompt_id=prompt_id, user_id=user_id)
            db.add(like)
            db_prompt.like_count += 1
            is_liked = True
        
        db_prompt.updated_at = datetime.utcnow()
        await db.commit()
        
        # Return the updated prompt in the standard format
        updated_prompt = await get_prompt(db, prompt_id, user_id=user_id)
        if not updated_prompt:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated prompt"
            )
            
        return updated_prompt
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in like_prompt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating like status: {str(e)}"
        )


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
