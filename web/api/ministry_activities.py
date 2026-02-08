from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import MinistryActivities, MinistryActivitiesCreate, MinistryActivitiesUpdate, MinistryActivitiesResponse
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/ministry-activities", tags=["ministry_activities"])


@router.post("/", response_model=MinistryActivitiesResponse)
async def create_activity(
    activity: MinistryActivitiesCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create a new ministry activity (current user becomes organizer)"""
    db_activity = MinistryActivities(
        title=activity.title,
        date=activity.date,
        is_regular=activity.is_regular,
        organizer_id=current_user_id,
        place=activity.place,
        outreach_id=activity.outreach_id,
        schedule_type=activity.schedule_type,
        weekdays=activity.weekdays,
        monthly_dates=activity.monthly_dates,
        yearly_dates=activity.yearly_dates,
        start_time=activity.start_time,
        end_time=activity.end_time
    )
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return db_activity


@router.get("/", response_model=list[MinistryActivitiesResponse])
async def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get all ministry activities"""
    result = await db.execute(
        select(MinistryActivities)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{activity_id}", response_model=MinistryActivitiesResponse)
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get a specific ministry activity"""
    result = await db.execute(
        select(MinistryActivities).where(MinistryActivities.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.put("/{activity_id}", response_model=MinistryActivitiesResponse)
async def update_activity(
    activity_id: int,
    activity_update: MinistryActivitiesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Update a ministry activity (only if organized by current user)"""
    result = await db.execute(
        select(MinistryActivities).where(MinistryActivities.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Only organizer can edit
    if activity.organizer_id != current_user_id:
        raise HTTPException(status_code=403, detail="Only organizer can update this activity")
    
    update_data = activity_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete a ministry activity (only if organized by current user)"""
    result = await db.execute(
        select(MinistryActivities).where(MinistryActivities.id == activity_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Only organizer can delete
    if activity.organizer_id != current_user_id:
        raise HTTPException(status_code=403, detail="Only organizer can delete this activity")
    
    await db.delete(activity)
    await db.commit()
