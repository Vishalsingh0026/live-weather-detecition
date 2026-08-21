import logging
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.database import get_db
from backend.models import Event, EventType
from backend.schemas import Event as EventSchema, EventCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[EventSchema])
async def get_events(
    skip: int = 0,
    limit: int = 50,
    event_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
):
    """Get all detected events with optional filtering."""
    try:
        query = select(Event).order_by(desc(Event.detected_at))

        if event_type:
            query = query.where(Event.event_type == EventType[event_type.upper()])

        if is_active is not None:
            query = query.where(Event.is_active == is_active)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        events = result.scalars().all()

        return events
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail="Error fetching events")


@router.get("/{event_id}", response_model=EventSchema)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific event by ID."""
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        event = result.scalar_one_or_none()

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching event")


@router.post("", response_model=EventSchema)
async def create_event(
    event: EventCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new event (manual or API-triggered)."""
    try:
        db_event = Event(
            event_type=event.event_type,
            location=event.location,
            latitude=event.latitude,
            longitude=event.longitude,
            severity=event.severity,
            confidence=event.confidence,
            description=event.description,
            data_source=event.data_source,
            raw_data=event.raw_data,
            detected_at=datetime.utcnow(),
        )

        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)

        logger.info(f"Event created with ID {db_event.id}")
        return db_event
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Error creating event")


@router.get("/stats/summary", response_model=dict)
async def get_events_summary(db: AsyncSession = Depends(get_db)):
    """Get summary statistics of all events."""
    try:
        # Get all active events
        result = await db.execute(select(Event).where(Event.is_active == True))
        all_events = result.scalars().all()

        total_events = len(all_events)
        critical_events = sum(1 for e in all_events if e.severity >= 85)
        high_severity = sum(1 for e in all_events if 70 <= e.severity < 85)

        avg_severity = (
            sum(e.severity for e in all_events) / len(all_events)
            if all_events
            else 0
        )

        # Event type breakdown
        type_breakdown = {}
        for event in all_events:
            event_type = event.event_type.value
            type_breakdown[event_type] = type_breakdown.get(event_type, 0) + 1

        return {
            "total_events": total_events,
            "critical_events": critical_events,
            "high_severity_events": high_severity,
            "average_severity": round(avg_severity, 2),
            "event_type_breakdown": type_breakdown,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting events summary: {e}")
        raise HTTPException(status_code=500, detail="Error getting summary")


@router.put("/{event_id}", response_model=EventSchema)
async def update_event(
    event_id: int,
    event_update: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update an event."""
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        db_event = result.scalar_one_or_none()

        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Update allowed fields
        for field, value in event_update.items():
            if hasattr(db_event, field) and field not in ["id", "created_at"]:
                setattr(db_event, field, value)

        db_event.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_event)

        logger.info(f"Event {event_id} updated")
        return db_event
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating event")


@router.delete("/{event_id}")
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Delete/deactivate an event."""
    try:
        result = await db.execute(select(Event).where(Event.id == event_id))
        db_event = result.scalar_one_or_none()

        if not db_event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Soft delete
        db_event.is_active = False
        db_event.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Event {event_id} deactivated")
        return {"message": "Event deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting event")
