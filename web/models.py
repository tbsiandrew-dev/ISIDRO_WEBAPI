from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Enum
from .database import Base
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import bcrypt
import enum as python_enum


# Password hashing utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# Enums
class DiscipleLevel(str, python_enum.Enum):
    PASTOR = "pastor"
    VINE = "vine"
    CLUSTER = "cluster"
    CARE_LEAD = "care_lead"
    DISCIPLE = "disciple"


# ============= USER MODELS =============
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= PERSONAL INFORMATION =============
class PersonalInformation(Base):
    __tablename__ = "personal_information"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)  # Male, Female, Other
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= DISCIPLE INFORMATION =============
class DiscipleInformation(Base):
    __tablename__ = "disciple_information"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, unique=True)
    level = Column(Enum(DiscipleLevel), nullable=False, default=DiscipleLevel.DISCIPLE)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Reference to mentor
    group_name = Column(String(100), nullable=True)
    joined_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= DEVOTION =============
class Devotion(Base):
    __tablename__ = "devotions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    scripture_reference = Column(String(100), nullable=True)
    devotion_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= TRAINING =============
class Training(Base):
    __tablename__ = "trainings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    trainer_name = Column(String(100), nullable=True)
    training_date = Column(DateTime(timezone=True), nullable=False)
    completion_status = Column(String(20), nullable=False, default="pending")  # pending, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= USER PYDANTIC SCHEMAS =============
class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, description="Password must be at least 8 characters")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= PERSONAL INFORMATION SCHEMAS =============
class PersonalInformationCreate(BaseModel):
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class PersonalInformationUpdate(BaseModel):
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class PersonalInformationResponse(BaseModel):
    id: int
    user_id: int
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= DISCIPLE INFORMATION SCHEMAS =============
class DiscipleInformationCreate(BaseModel):
    level: DiscipleLevel = DiscipleLevel.DISCIPLE
    mentor_id: Optional[int] = None
    group_name: Optional[str] = None
    joined_date: Optional[datetime] = None


class DiscipleInformationUpdate(BaseModel):
    level: Optional[DiscipleLevel] = None
    mentor_id: Optional[int] = None
    group_name: Optional[str] = None
    joined_date: Optional[datetime] = None


class DiscipleInformationResponse(BaseModel):
    id: int
    user_id: int
    level: DiscipleLevel
    mentor_id: Optional[int] = None
    group_name: Optional[str] = None
    joined_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= DEVOTION SCHEMAS =============
class DevotionCreate(BaseModel):
    title: str
    content: str
    scripture_reference: Optional[str] = None
    devotion_date: datetime


class DevotionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    scripture_reference: Optional[str] = None
    devotion_date: Optional[datetime] = None


class DevotionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    scripture_reference: Optional[str] = None
    devotion_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= TRAINING SCHEMAS =============
class TrainingCreate(BaseModel):
    title: str
    description: str
    trainer_name: Optional[str] = None
    training_date: datetime
    notes: Optional[str] = None


class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    trainer_name: Optional[str] = None
    training_date: Optional[datetime] = None
    completion_status: Optional[str] = None
    notes: Optional[str] = None


class TrainingResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    trainer_name: Optional[str] = None
    training_date: datetime
    completion_status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
