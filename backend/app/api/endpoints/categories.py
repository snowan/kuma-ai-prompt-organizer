from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.CategoryResponse])
async def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all categories.
    """
    categories = await crud.get_categories(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=schemas.CategoryResponse, status_code=201)
async def create_category(
    category: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category.
    """
    # Check if category with this name already exists
    db_category = await crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=400, 
            detail="Category with this name already exists"
        )
    
    return await crud.create_category(db=db, category=category)

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def read_category(
    category_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific category by ID.
    """
    db_category = await crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: int,
    category: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a category.
    """
    # Check if category exists
    db_category = await crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if new name is already taken by another category
    if category.name is not None:
        existing_category = await crud.get_category_by_name(db, name=category.name)
        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=400, 
                detail="Category with this name already exists"
            )
    
    return await crud.update_category(
        db=db, 
        category_id=category_id, 
        category=category
    )

@router.delete("/{category_id}", response_model=schemas.CategoryResponse)
async def delete_category(
    category_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a category.
    """
    db_category = await crud.delete_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category
