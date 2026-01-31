"""Training API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..models import Training, TrainingCreate, TrainingUpdate, TrainingResponse

router = APIRouter(prefix="/api/trainings", tags=["trainings"])


@router.post("/{user_id}", response_model=TrainingResponse, status_code=201)
async def create_training(user_id: int, training: TrainingCreate, db: AsyncSession = Depends(get_db)):
    """Create a training for a user"""
    # Check if user exists
    from ..models import User
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    
    db_training = Training(user_id=user_id, **training.dict())
    db.add(db_training)
    await db.flush()
    await db.refresh(db_training)
    return db_training


@router.get("/{user_id}", response_model=List[TrainingResponse])
async def get_user_trainings(user_id: int, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all trainings for a user"""
    result = await db.execute(
        select(Training).where(Training.user_id == user_id).offset(skip).limit(limit)
    )
    trainings = result.scalars().all()
    return trainings


@router.get("/{user_id}/{training_id}", response_model=TrainingResponse)
async def get_training(user_id: int, training_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific training"""
    result = await db.execute(
        select(Training).where(Training.id == training_id, Training.user_id == user_id)
    )
    training = result.scalar_one_or_none()
    
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    
    return training


@router.put("/{user_id}/{training_id}", response_model=TrainingResponse)
async def update_training(user_id: int, training_id: int, training_update: TrainingUpdate, db: AsyncSession = Depends(get_db)):
    """Update a training"""
    result = await db.execute(
        select(Training).where(Training.id == training_id, Training.user_id == user_id)
    )
    training = result.scalar_one_or_none()
    
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    
    update_data = training_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(training, field, value)
    
    await db.flush()
    await db.refresh(training)
    return training


@router.delete("/{user_id}/{training_id}", status_code=204)
async def delete_training(user_id: int, training_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a training"""
    result = await db.execute(
        select(Training).where(Training.id == training_id, Training.user_id == user_id)
    )
    training = result.scalar_one_or_none()
    
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    
    await db.delete(training)
    return None
