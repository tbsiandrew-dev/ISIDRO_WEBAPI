from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# SQLAlchemy Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Pydantic Schemas for request/response
class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
