from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models
from app.api.deps.auth import get_current_active_user
from app.database import get_db
from app.schemas.auth import LikeResponse
from app.models import UserLike

router = APIRouter()

@router.post("/prompts/{prompt_id}/like", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def like_prompt(
    prompt_id: int,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Like a prompt."""
    # Check if prompt exists
    result = await db.execute(
        select(models.Prompt).where(models.Prompt.id == prompt_id)
    )
    prompt = result.scalars().first()
    
    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Check if user already liked the prompt
    result = await db.execute(
        select(UserLike).where(
            UserLike.user_id == current_user.id,
            UserLike.prompt_id == prompt_id
        )
    )
    existing_like = result.scalars().first()
    
    if existing_like is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this prompt"
        )
    
    # Create new like
    db_like = UserLike(
        user_id=current_user.id,
        prompt_id=prompt_id
    )
    
    # Update like count
    prompt.like_count += 1
    
    db.add(db_like)
    await db.commit()
    await db.refresh(db_like)
    
    return db_like

@router.delete("/prompts/{prompt_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_prompt(
    prompt_id: int,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Remove a like from a prompt."""
    # Check if prompt exists
    result = await db.execute(
        select(models.Prompt).where(models.Prompt.id == prompt_id)
    )
    prompt = result.scalars().first()
    
    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Check if user has liked the prompt
    result = await db.execute(
        select(UserLike).where(
            UserLike.user_id == current_user.id,
            UserLike.prompt_id == prompt_id
        )
    )
    like = result.scalars().first()
    
    if like is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this prompt"
        )
    
    # Update like count
    if prompt.like_count > 0:
        prompt.like_count -= 1
    
    # Remove like
    await db.delete(like)
    await db.commit()

@router.get("/prompts/{prompt_id}/liked", response_model=bool)
async def check_if_liked(
    prompt_id: int,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Check if the current user has liked a prompt."""
    result = await db.execute(
        select(UserLike).where(
            UserLike.user_id == current_user.id,
            UserLike.prompt_id == prompt_id
        )
    )
    like = result.scalars().first()
    return like is not None

@router.get("/users/me/likes", response_model=list[LikeResponse])
async def get_user_likes(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get all likes by the current user."""
    result = await db.execute(
        select(UserLike)
        .where(UserLike.user_id == current_user.id)
        .order_by(UserLike.created_at.desc())
    )
    return result.scalars().all()
