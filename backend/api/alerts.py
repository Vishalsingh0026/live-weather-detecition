import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.database import get_db
from backend.models import Alert, AlertSeverity
from backend.schemas import Alert as AlertSchema, AlertCreate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[AlertSchema])
async def get_alerts(
    skip: int = 0,
    limit: int = 50,
    severity: Optional[str] = None,
    is_sent: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all alerts with optional filtering."""
    try:
        query = select(Alert).order_by(desc(Alert.created_at))

        if severity:
            query = query.where(Alert.severity == AlertSeverity[severity.upper()])

        if is_sent is not None:
            query = query.where(Alert.is_sent == is_sent)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        alerts = result.scalars().all()

        return alerts
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Error fetching alerts")


@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific alert by ID."""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return alert
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching alert")


@router.post("", response_model=AlertSchema)
async def create_alert(
    alert: AlertCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new alert."""
    try:
        db_alert = Alert(
            event_id=alert.event_id,
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            recipient_emails=alert.recipient_emails,
        )

        db.add(db_alert)
        await db.commit()
        await db.refresh(db_alert)

        logger.info(f"Alert created with ID {db_alert.id}")
        return db_alert
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Error creating alert")


@router.put("/{alert_id}/send", response_model=AlertSchema)
async def send_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Mark alert as sent."""
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        db_alert = result.scalar_one_or_none()

        if not db_alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        db_alert.is_sent = True
        db_alert.sent_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_alert)

        logger.info(f"Alert {alert_id} marked as sent")
        return db_alert
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error sending alert {alert_id}: {e}")
        raise HTTPException(status_code=500, detail="Error sending alert")


@router.get("/stats/critical", response_model=dict)
async def get_critical_alerts(db: AsyncSession = Depends(get_db)):
    """Get critical alerts statistics."""
    try:
        result = await db.execute(
            select(Alert).where(Alert.severity == AlertSeverity.CRITICAL)
        )
        critical_alerts = result.scalars().all()

        unsent = sum(1 for a in critical_alerts if not a.is_sent)

        return {
            "total_critical": len(critical_alerts),
            "unsent": unsent,
            "sent": len(critical_alerts) - unsent,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting critical alerts: {e}")
        raise HTTPException(status_code=500, detail="Error getting critical alerts")
