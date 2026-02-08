from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date
from ..models import AttendanceInformation, AttendanceInformationCreate, AttendanceInformationUpdate, AttendanceInformationResponse
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.post("/", response_model=AttendanceInformationResponse)
async def create_attendance(
    attendance: AttendanceInformationCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create a new attendance record for current user"""
    db_attendance = AttendanceInformation(
        user_id=current_user_id,
        date=attendance.date,
        time_in=attendance.time_in,
        is_present=attendance.is_present,
        ministry_activity_id=attendance.ministry_activity_id,
        ministry_type=attendance.ministry_type,
        training_id=attendance.training_id
    )
    db.add(db_attendance)
    await db.commit()
    await db.refresh(db_attendance)
    return db_attendance


@router.get("/", response_model=list[AttendanceInformationResponse])
async def get_user_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get all attendance records for current user"""
    result = await db.execute(
        select(AttendanceInformation)
        .where(AttendanceInformation.user_id == current_user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{attendance_id}", response_model=AttendanceInformationResponse)
async def get_attendance(
    attendance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get a specific attendance record (only if it belongs to current user)"""
    result = await db.execute(
        select(AttendanceInformation).where(
            and_(
                AttendanceInformation.id == attendance_id,
                AttendanceInformation.user_id == current_user_id
            )
        )
    )
    attendance = result.scalar_one_or_none()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceInformationResponse)
async def update_attendance(
    attendance_id: int,
    attendance_update: AttendanceInformationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Update an attendance record (only if it belongs to current user)"""
    result = await db.execute(
        select(AttendanceInformation).where(
            and_(
                AttendanceInformation.id == attendance_id,
                AttendanceInformation.user_id == current_user_id
            )
        )
    )
    attendance = result.scalar_one_or_none()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    update_data = attendance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    
    db.add(attendance)
    await db.commit()
    await db.refresh(attendance)
    return attendance


@router.delete("/{attendance_id}", status_code=204)
async def delete_attendance(
    attendance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete an attendance record (only if it belongs to current user)"""
    result = await db.execute(
        select(AttendanceInformation).where(
            and_(
                AttendanceInformation.id == attendance_id,
                AttendanceInformation.user_id == current_user_id
            )
        )
    )
    attendance = result.scalar_one_or_none()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    await db.delete(attendance)
    await db.commit()
