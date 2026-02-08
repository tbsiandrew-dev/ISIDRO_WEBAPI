from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Outreach, OutreachCreate, OutreachUpdate, OutreachResponse
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.post("/", response_model=OutreachResponse)
async def create_outreach(
    outreach: OutreachCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create a new outreach program"""
    db_outreach = Outreach(
        name=outreach.name,
        assigned_pastor=outreach.assigned_pastor,
        location=outreach.location,
        year_start=outreach.year_start
    )
    db.add(db_outreach)
    await db.commit()
    await db.refresh(db_outreach)
    return db_outreach


@router.get("/", response_model=list[OutreachResponse])
async def get_outreaches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get all outreach programs"""
    result = await db.execute(
        select(Outreach)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{outreach_id}", response_model=OutreachResponse)
async def get_outreach(
    outreach_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get a specific outreach program"""
    result = await db.execute(
        select(Outreach).where(Outreach.id == outreach_id)
    )
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach program not found")
    return outreach


@router.put("/{outreach_id}", response_model=OutreachResponse)
async def update_outreach(
    outreach_id: int,
    outreach_update: OutreachUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Update an outreach program (only if assigned to current user)"""
    result = await db.execute(
        select(Outreach).where(Outreach.id == outreach_id)
    )
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach program not found")
    
    # Only assigned pastor can edit
    if outreach.assigned_pastor != current_user_id:
        raise HTTPException(status_code=403, detail="Only assigned pastor can update this outreach")
    
    update_data = outreach_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(outreach, field, value)
    
    db.add(outreach)
    await db.commit()
    await db.refresh(outreach)
    return outreach


@router.delete("/{outreach_id}", status_code=204)
async def delete_outreach(
    outreach_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Delete an outreach program (only if assigned to current user)"""
    result = await db.execute(
        select(Outreach).where(Outreach.id == outreach_id)
    )
    outreach = result.scalar_one_or_none()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach program not found")
    
    # Only assigned pastor can delete
    if outreach.assigned_pastor != current_user_id:
        raise HTTPException(status_code=403, detail="Only assigned pastor can delete this outreach")
    
    await db.delete(outreach)
    await db.commit()
