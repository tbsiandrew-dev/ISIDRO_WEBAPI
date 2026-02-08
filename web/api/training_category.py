from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import TrainingCategory, TrainingCategoryCreate, TrainingCategoryUpdate, TrainingCategoryResponse
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/training-categories", tags=["training_categories"])


@router.post("/", response_model=TrainingCategoryResponse)
async def create_category(
    category: TrainingCategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create a new training category (admin only)"""
    db_category = TrainingCategory(
        name=category.name,
        type=category.type
    )
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.get("/", response_model=list[TrainingCategoryResponse])
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get all training categories"""
    result = await db.execute(
        select(TrainingCategory)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{category_id}", response_model=TrainingCategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get a specific training category"""
    result = await db.execute(
        select(TrainingCategory).where(TrainingCategory.id == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=TrainingCategoryResponse)
async def update_category(
    category_id: int,
    category_update: TrainingCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Update a training category (admin only)"""
    result = await db.execute(
        select(TrainingCategory).where(TrainingCategory.id == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete a training category (admin only)"""
    result = await db.execute(
        select(TrainingCategory).where(TrainingCategory.id == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await db.delete(category)
    await db.commit()
