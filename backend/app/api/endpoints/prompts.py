from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Set
from sqlalchemy import update, select, func, and_
from sqlalchemy.orm import selectinload

from app import crud, schemas, models
from app.database import get_db
from app.core import get_user_id_from_request, security
from app.models import Prompt, Category, Tag, PromptLike

# For endpoints that require authentication, we can use:
# current_user_id: str = Depends(security.get_current_user_id)

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
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve prompts with optional filtering and search.
    Includes like status for the current user if authenticated.
    """
    # Get current user ID from the request (if authenticated)
    current_user_id = get_user_id_from_request(request)
    
    # Get prompts with base filters and like status
    prompts = await crud.get_prompts(
        db, 
        skip=skip, 
        limit=limit, 
        search=search,
        user_id=current_user_id
    )
    
    # Apply additional filters
    if category_id is not None:
        prompts = [p for p in prompts if p.category_id == category_id]
    
    if tag is not None:
        tag_lower = tag.lower()
        prompts = [p for p in prompts if any(
            t.name.lower() == tag_lower 
            for t in (p.tags or [])
        )]
    
    return prompts

@router.post("/", response_model=schemas.PromptResponse, status_code=201)
async def create_prompt(
    prompt: schemas.PromptCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new prompt with optional category and tags.
    """
    try:
        # Get current user ID from the request (if authenticated)
        current_user_id = get_user_id_from_request(request)
        
        # Check if category exists if provided
        if prompt.category_id is not None:
            db_category = await crud.get_category(db, category_id=prompt.category_id)
            if not db_category:
                raise HTTPException(status_code=400, detail="Category not found")
        
        # Create prompt (handles duplicate checking)
        result = await crud.create_prompt(db=db, prompt=prompt, user_id=current_user_id)
        
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
async def read_prompt(
    prompt_id: int, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific prompt by ID.
    Includes like status for the current user if authenticated.
    """
    # Get current user ID from the request (if authenticated)
    current_user_id = get_user_id_from_request(request)
    
    # Get prompt with like status for the current user
    db_prompt = await crud.get_prompt(
        db, 
        prompt_id=prompt_id,
        user_id=current_user_id
    )
    
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return db_prompt

@router.put("/{prompt_id}", response_model=schemas.PromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt: schemas.PromptUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a prompt.
    """
    # Get current user ID from the request (if authenticated)
    current_user_id = get_user_id_from_request(request)
    
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
    result = await crud.update_prompt(db=db, prompt_id=prompt_id, prompt=prompt, user_id=current_user_id)
    
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
    prompt_id: int, 
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a prompt.
    """
    # Get current user ID from the request (if authenticated)
    current_user_id = get_user_id_from_request(request)
    
    prompt = await crud.get_prompt(db, prompt_id=prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return await crud.delete_prompt(db=db, prompt_id=prompt_id, user_id=current_user_id)

@router.post("/{prompt_id}/like", response_model=schemas.PromptResponse)
async def like_prompt(
    prompt_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Like or unlike a prompt for the current user.
    Returns the updated prompt with the new like count and like status.
    """
    # Get current user ID from the request (if authenticated)
    current_user_id = get_user_id_from_request(request)
    
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        # Toggle like status and get updated prompt
        updated_prompt = await crud.like_prompt(db, prompt_id, current_user_id)
        
        # Ensure the response includes all necessary data
        return await crud.get_prompt(
            db, 
            prompt_id=prompt_id,
            user_id=current_user_id
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the like status"
        )

@router.get("/{prompt_id}/likes", response_model=schemas.LikeResponse)
async def get_prompt_likes(
    prompt_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the like count and like status for a prompt.
    """
    # Get current user ID from the request (if authenticated)
    current_user_id = get_user_id_from_request(request)
    
    # Check if prompt exists
    prompt = await crud.get_prompt(db, prompt_id=prompt_id, user_id=current_user_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return {
        "count": prompt.like_count,
        "is_liked": prompt.is_liked if hasattr(prompt, 'is_liked') else False
    }

@router.get("/user/likes", response_model=List[int])
async def get_user_liked_prompts(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all prompt IDs that the current user has liked.
    """
    # Get current user ID from the request (if authenticated)
    current_user_id = get_user_id_from_request(request)
    
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        liked_prompt_ids = await crud.get_user_liked_prompt_ids(db, current_user_id)
        return list(liked_prompt_ids)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching liked prompts"
        )
