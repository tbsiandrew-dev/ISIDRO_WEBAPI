from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Enum, Date, Boolean
from .database import Base
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
import bcrypt
import enum as python_enum


# Export all models for alembic auto-discovery
__all__ = [
    'User',
    'PersonalInformation',
    'DiscipleInformation',
    'Devotion',
    'Training',
    'TrainingCategory',
    'MinistryActivities',
    'AttendanceInformation',
    'Outreach',
]


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


class ScheduleType(str, python_enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class MinistryType(str, python_enum.Enum):
    DISCIPLESHIP = "discipleship"
    TRAINING = "training"
    CELEBRATION = "celebration"
    EVANGELISM = "evangelism"


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
    first_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    birthday = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)  # Male, Female, Other
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    profile_image = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= MINISTRY ACTIVITIES =============
class MinistryActivities(Base):
    __tablename__ = "ministry_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    is_regular = Column(Boolean, default=False)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    place = Column(String(255), nullable=True)
    outreach_id = Column(Integer, ForeignKey("outreach.id"), nullable=True)
    schedule_type = Column(Enum(ScheduleType), nullable=False, default=ScheduleType.DAILY)
    weekdays = Column(String(255), nullable=True)  # "SUN,WED,TUE" or "0,3,2" for weekly schedules
    monthly_dates = Column(String(255), nullable=True)  # "1,15" for 1st and 15th of month
    yearly_dates = Column(String(255), nullable=True)  # "01-01,12-25" for Jan 1 and Dec 25 (MM-DD format)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= ATTENDANCE INFORMATION =============
class AttendanceInformation(Base):
    __tablename__ = "attendance_information"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    time_in = Column(DateTime(timezone=True), nullable=False)
    is_present = Column(Boolean, default=True)
    ministry_activity_id = Column(Integer, ForeignKey("ministry_activities.id"), nullable=False)
    ministry_type = Column(Enum(MinistryType), nullable=False)  # discipleship, training, celebration, evangelism
    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=True)  # Only for training type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= TRAINING CATEGORY =============
class TrainingCategory(Base):
    __tablename__ = "training_category"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # discipleship, seminar
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============= OUTREACH =============
class Outreach(Base):
    __tablename__ = "outreach"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    assigned_pastor = Column(Integer, ForeignKey("users.id"), nullable=False)
    location = Column(String(255), nullable=False)
    year_start = Column(Integer, nullable=False)
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
    outreach_id = Column(Integer, ForeignKey("outreach.id"), nullable=True)
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
    category_id = Column(Integer, ForeignKey("training_category.id"), nullable=True)
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
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None


class PersonalInformationUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None


class PersonalInformationResponse(BaseModel):
    id: int
    user_id: int
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
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
    outreach_id: Optional[int] = None


class DiscipleInformationUpdate(BaseModel):
    level: Optional[DiscipleLevel] = None
    mentor_id: Optional[int] = None
    group_name: Optional[str] = None
    joined_date: Optional[datetime] = None
    outreach_id: Optional[int] = None


class DiscipleInformationResponse(BaseModel):
    id: int
    user_id: int
    level: DiscipleLevel
    mentor_id: Optional[int] = None
    group_name: Optional[str] = None
    joined_date: Optional[datetime] = None
    outreach_id: Optional[int] = None
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
    completion_status: str = "pending"
    category_id: Optional[int] = None
    notes: Optional[str] = None


class TrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    trainer_name: Optional[str] = None
    training_date: Optional[datetime] = None
    completion_status: Optional[str] = None
    category_id: Optional[int] = None
    notes: Optional[str] = None


class TrainingResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    trainer_name: Optional[str] = None
    training_date: datetime
    completion_status: str
    category_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= TRAINING CATEGORY SCHEMAS =============
class TrainingCategoryCreate(BaseModel):
    name: str
    type: str  # discipleship, seminar


class TrainingCategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class TrainingCategoryResponse(BaseModel):
    id: int
    name: str
    type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= MINISTRY ACTIVITIES SCHEMAS =============
class MinistryActivitiesCreate(BaseModel):
    title: str
    date: datetime
    is_regular: bool = False
    organizer_id: int
    place: Optional[str] = None
    outreach_id: Optional[int] = None
    schedule_type: str = "daily"  # daily, weekly, monthly, yearly
    weekdays: Optional[str] = None  # "SUN,WED,TUE" or "0,3,2" for weekly schedules
    monthly_dates: Optional[str] = None  # "1,15" for 1st and 15th of month
    yearly_dates: Optional[str] = None  # "01-01,12-25" for Jan 1 and Dec 25 (MM-DD format)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class MinistryActivitiesUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    is_regular: Optional[bool] = None
    organizer_id: Optional[int] = None
    place: Optional[str] = None
    outreach_id: Optional[int] = None
    schedule_type: Optional[str] = None
    weekdays: Optional[str] = None
    monthly_dates: Optional[str] = None
    yearly_dates: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class MinistryActivitiesResponse(BaseModel):
    id: int
    title: str
    date: datetime
    is_regular: bool
    organizer_id: int
    place: Optional[str] = None
    outreach_id: Optional[int] = None
    schedule_type: str
    weekdays: Optional[str] = None
    monthly_dates: Optional[str] = None
    yearly_dates: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= ATTENDANCE INFORMATION SCHEMAS =============
class AttendanceInformationCreate(BaseModel):
    date: date
    time_in: datetime
    is_present: bool = True
    ministry_activity_id: int
    ministry_type: str  # discipleship, training, celebration, evangelism
    training_id: Optional[int] = None  # Only for training type


class AttendanceInformationUpdate(BaseModel):
    date: Optional[date] = None
    time_in: Optional[datetime] = None
    is_present: Optional[bool] = None
    ministry_activity_id: Optional[int] = None
    ministry_type: Optional[str] = None
    training_id: Optional[int] = None


class AttendanceInformationResponse(BaseModel):
    id: int
    user_id: int
    date: date
    time_in: datetime
    is_present: bool
    ministry_activity_id: int
    ministry_type: str
    training_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= OUTREACH SCHEMAS =============
class OutreachCreate(BaseModel):
    name: str
    assigned_pastor: int
    location: str
    year_start: int


class OutreachUpdate(BaseModel):
    name: Optional[str] = None
    assigned_pastor: Optional[int] = None
    location: Optional[str] = None
    year_start: Optional[int] = None


class OutreachResponse(BaseModel):
    id: int
    name: str
    assigned_pastor: int
    location: str
    year_start: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
