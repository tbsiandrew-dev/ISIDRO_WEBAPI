"""Personal Information API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..dependencies import get_current_user
from ..models import PersonalInformation, PersonalInformationCreate, PersonalInformationUpdate, PersonalInformationResponse

router = APIRouter(prefix="/api/personal-info", tags=["personal-information"])


@router.post("/{user_id}", response_model=PersonalInformationResponse, status_code=201)
async def create_personal_info(
    user_id: int,
    info: PersonalInformationCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create personal information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own information")
    
    # Check if user exists
    from ..models import User
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    
    db_info = PersonalInformation(user_id=user_id, **info.dict())
    db.add(db_info)
    await db.flush()
    await db.refresh(db_info)
    return db_info


@router.get("/{user_id}", response_model=PersonalInformationResponse)
async def get_personal_info(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get personal information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only access your own information")
    
    result = await db.execute(select(PersonalInformation).where(PersonalInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Personal information not found")
    
    return info


@router.put("/{user_id}", response_model=PersonalInformationResponse)
async def update_personal_info(
    user_id: int,
    info_update: PersonalInformationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Update personal information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only update your own information")
    
    result = await db.execute(select(PersonalInformation).where(PersonalInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Personal information not found")
    
    update_data = info_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(info, field, value)
    
    await db.flush()
    await db.refresh(info)
    return info


@router.delete("/{user_id}", status_code=204)
async def delete_personal_info(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete personal information for a user (requires JWT token)"""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own information")
    
    result = await db.execute(select(PersonalInformation).where(PersonalInformation.user_id == user_id))
    info = result.scalar_one_or_none()
    
    if not info:
        raise HTTPException(status_code=404, detail="Personal information not found")
    
    await db.delete(info)
    return None
