from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.TagResponse])
async def read_tags(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all tags.
    """
    tags = await crud.get_tags(db, skip=skip, limit=limit)
    return tags

@router.get("/{tag_id}", response_model=schemas.TagResponse)
async def read_tag(
    tag_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific tag by ID.
    """
    db_tag = await crud.get_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@router.delete("/{tag_id}", response_model=schemas.TagResponse)
async def delete_tag(
    tag_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a tag.
    Note: This will remove the tag from all prompts but won't delete the prompts themselves.
    """
    db_tag = await crud.delete_tag(db, tag_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag
