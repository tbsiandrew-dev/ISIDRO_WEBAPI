"""Disciple Information API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..dependencies import get_current_user
from ..models import DiscipleInformation, DiscipleInformationCreate, DiscipleInformationUpdate, DiscipleInformationResponse

router = APIRouter(prefix="/api/disciple-info", tags=["disciple-information"])


@router.post("/{user_id}", response_model=DiscipleInformationResponse, status_code=201)
async def create_disciple_info(
    user_id: int,
    info: DiscipleInformationCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create disciple information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own information")
    
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
async def get_disciple_info(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get disciple information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own information")
    
    result = await db.execute(select(DiscipleInformation).where(DiscipleInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Disciple information not found")
    
    return info


@router.put("/{user_id}", response_model=DiscipleInformationResponse)
async def update_disciple_info(
    user_id: int,
    info_update: DiscipleInformationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Update disciple information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only update your own information")
    
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
async def delete_disciple_info(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete disciple information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own information")
    
    result = await db.execute(select(DiscipleInformation).where(DiscipleInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Disciple information not found")
    
    await db.delete(info)
    return None
