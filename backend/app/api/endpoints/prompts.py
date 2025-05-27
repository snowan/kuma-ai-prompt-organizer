from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from sqlalchemy import update, select, func
from sqlalchemy.orm import selectinload
from app.models import Prompt, Category, Tag

from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for the dashboard.
    """
    # Get total counts
    total_prompts = (await db.execute(select(func.count(Prompt.id)))).scalar() or 0
    total_categories = (await db.execute(select(func.count(Category.id)))).scalar() or 0
    total_tags = (await db.execute(select(func.count(Tag.id)))).scalar() or 0
    
    # Get prompts by category
    categories = (await db.execute(
        select(Category)
        .options(selectinload(Category.prompts))
    )).scalars().all()
    
    prompts_by_category = {
        category.name: len(category.prompts)
        for category in categories
    }
    
    return {
        "total_prompts": total_prompts,
        "total_categories": total_categories,
        "total_tags": total_tags,
        "prompts_by_category": prompts_by_category
    }

@router.get("/", response_model=List[schemas.PromptResponse])
async def read_prompts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve prompts with optional filtering and search.
    """
    # Get prompts with base filters
    prompts = await crud.get_prompts(db, skip=skip, limit=limit, search=search)
    
    # Apply additional filters
    if category_id is not None:
        prompts = [p for p in prompts if p.category_id == category_id]
    
    if tag is not None:
        tag_lower = tag.lower()
        prompts = [p for p in prompts if any(t.name.lower() == tag_lower for t in p.tags)]
    
    return prompts

@router.post("/", response_model=schemas.PromptResponse, status_code=201)
async def create_prompt(
    prompt: schemas.PromptCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new prompt with optional category and tags.
    """
    try:
        # Check if category exists if provided
        if prompt.category_id is not None:
            db_category = await crud.get_category(db, category_id=prompt.category_id)
            if not db_category:
                raise HTTPException(status_code=400, detail="Category not found")
        
        # Create prompt (handles duplicate checking)
        # TODO: Get user_id from authentication context
        result = await crud.create_prompt(db=db, prompt=prompt, user_id=1)
        
        # Handle case where a similar prompt was found
        if isinstance(result, dict) and 'similar_prompt_id' in result:
            raise HTTPException(
                status_code=400,
                detail={
                    "detail": "A similar prompt already exists",
                    "similar_prompt_id": result["similar_prompt_id"],
                    "similarity": result["similarity"]
                }
            )
            
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create prompt")
            
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{prompt_id}", response_model=schemas.PromptResponse)
async def read_prompt(prompt_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific prompt by ID.
    """
    db_prompt = await crud.get_prompt(db, prompt_id=prompt_id)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt

@router.put("/{prompt_id}", response_model=schemas.PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt: schemas.PromptUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a prompt.
    """
    # Check if prompt exists
    db_prompt = await crud.get_prompt(db, prompt_id=prompt_id)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Check if new category exists if provided
    if prompt.category_id is not None:
        db_category = await crud.get_category(db, category_id=prompt.category_id)
        if not db_category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # Update prompt (handles duplicate checking)
    result = await crud.update_prompt(db=db, prompt_id=prompt_id, prompt=prompt)
    
    # Check if result is a duplicate warning
    if isinstance(result, dict) and "similar_prompt_id" in result:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "A similar prompt already exists",
                "similar_prompt_id": result["similar_prompt_id"],
                "similarity": result["similarity"]
            }
        )
    
    return result

@router.delete("/{prompt_id}", response_model=schemas.PromptResponse)
async def delete_prompt(
    prompt_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Delete a prompt.
    """
    prompt = await crud.get_prompt(db, prompt_id=prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return await crud.delete_prompt(db=db, prompt_id=prompt_id)

@router.post("/{prompt_id}/like", response_model=schemas.PromptResponse)
async def like_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Increment the like count for a prompt.
    """
    # Check if prompt exists
    result = await db.execute(select(Prompt).filter(Prompt.id == prompt_id))
    prompt = result.scalars().first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Increment the like count
    stmt = (
        update(Prompt)
        .where(Prompt.id == prompt_id)
        .values(likes=Prompt.likes + 1)
        .returning(Prompt)
    )
    
    result = await db.execute(stmt)
    updated_prompt = result.scalars().first()
    await db.commit()
    
    # Refresh to get updated relationships
    await db.refresh(updated_prompt, ['category', 'tags'])
    
    return updated_prompt
