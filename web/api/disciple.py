"""Disciple Information API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import DiscipleInformation, DiscipleInformationCreate, DiscipleInformationUpdate, DiscipleInformationResponse

router = APIRouter(prefix="/api/disciple-info", tags=["disciple-information"])


@router.post("/{user_id}", response_model=DiscipleInformationResponse, status_code=201)
async def create_disciple_info(user_id: int, info: DiscipleInformationCreate, db: AsyncSession = Depends(get_db)):
    """Create disciple information for a user"""
    # Check if user exists
    from ..models import User
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if disciple info already exists
    existing = await db.execute(select(DiscipleInformation).where(DiscipleInformation.user_id == user_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Disciple information already exists for this user")
    
    db_info = DiscipleInformation(user_id=user_id, **info.dict())
    db.add(db_info)
    await db.flush()
    await db.refresh(db_info)
    return db_info


@router.get("/{user_id}", response_model=DiscipleInformationResponse)
async def get_disciple_info(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get disciple information for a user"""
    result = await db.execute(select(DiscipleInformation).where(DiscipleInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Disciple information not found")
    
    return info


@router.put("/{user_id}", response_model=DiscipleInformationResponse)
async def update_disciple_info(user_id: int, info_update: DiscipleInformationUpdate, db: AsyncSession = Depends(get_db)):
    """Update disciple information for a user"""
    result = await db.execute(select(DiscipleInformation).where(DiscipleInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Disciple information not found")
    
    update_data = info_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(info, field, value)
    
    await db.flush()
    await db.refresh(info)
    return info


@router.delete("/{user_id}", status_code=204)
async def delete_disciple_info(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete disciple information for a user"""
    result = await db.execute(select(DiscipleInformation).where(DiscipleInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Disciple information not found")
    
    await db.delete(info)
    return None
