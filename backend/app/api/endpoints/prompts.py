from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

router = APIRouter()

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
    # Check if category exists if provided
    if prompt.category_id is not None:
        db_category = await crud.get_category(db, category_id=prompt.category_id)
        if not db_category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # Create prompt (handles duplicate checking)
    result = await crud.create_prompt(db=db, prompt=prompt)
    
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
async def delete_prompt(prompt_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a prompt.
    """
    db_prompt = await crud.delete_prompt(db, prompt_id=prompt_id)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt
