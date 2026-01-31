from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, UserCreate, UserUpdate, UserResponse
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    
    return db_user


@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all users"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Update a user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields if provided
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        # Check if new email already exists
        email_check = await db.execute(
            select(User).where(User.email == user_update.email, User.id != user_id)
        )
        if email_check.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_update.email
    
    await db.flush()
    await db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a user"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    return None
