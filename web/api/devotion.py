"""Devotion API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..dependencies import get_current_user
from ..models import Devotion, DevotionCreate, DevotionUpdate, DevotionResponse

router = APIRouter(prefix="/api/devotions", tags=["devotions"])


@router.post("/{user_id}", response_model=DevotionResponse, status_code=201)
async def create_devotion(
    user_id: int,
    devotion: DevotionCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create a devotion for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own information")
    
    # Check if user exists
    from ..models import User
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    
    db_devotion = Devotion(user_id=user_id, **devotion.dict())
    db.add(db_devotion)
    await db.flush()
    await db.refresh(db_devotion)
    return db_devotion


@router.get("/{user_id}", response_model=List[DevotionResponse])
async def get_user_devotions(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get all devotions for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own information")
    
    result = await db.execute(
        select(Devotion).where(Devotion.user_id == user_id).offset(skip).limit(limit)
    )
    devotions = result.scalars().all()
    return devotions


@router.get("/{user_id}/{devotion_id}", response_model=DevotionResponse)
async def get_devotion(
    user_id: int,
    devotion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get a specific devotion (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own information")
    
    result = await db.execute(
        select(Devotion).where(Devotion.id == devotion_id, Devotion.user_id == user_id)
    )
    devotion = result.scalar_one_or_none()
    
    if not devotion:
        raise HTTPException(status_code=404, detail="Devotion not found")
    
    return devotion


@router.put("/{user_id}/{devotion_id}", response_model=DevotionResponse)
async def update_devotion(
    user_id: int,
    devotion_id: int,
    devotion_update: DevotionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Update a devotion (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only update your own information")
    
    result = await db.execute(
        select(Devotion).where(Devotion.id == devotion_id, Devotion.user_id == user_id)
    )
    devotion = result.scalar_one_or_none()
    
    if not devotion:
        raise HTTPException(status_code=404, detail="Devotion not found")
    
    update_data = devotion_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(devotion, field, value)
    
    await db.flush()
    await db.refresh(devotion)
    return devotion


@router.delete("/{user_id}/{devotion_id}", status_code=204)
async def delete_devotion(
    user_id: int,
    devotion_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete a devotion (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own information")
    
    result = await db.execute(
        select(Devotion).where(Devotion.id == devotion_id, Devotion.user_id == user_id)
    )
    devotion = result.scalar_one_or_none()
    
    if not devotion:
        raise HTTPException(status_code=404, detail="Devotion not found")
    
    await db.delete(devotion)
    return None
