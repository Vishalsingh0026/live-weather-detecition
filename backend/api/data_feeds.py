import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.database import get_db
from backend.models import DataFeed, RawDataPoint
from backend.schemas import DataFeed as DataFeedSchema, DataFeedCreate, RawDataPoint as RawDataPointSchema

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[DataFeedSchema])
async def get_data_feeds(
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = True,
    feed_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all data feeds with optional filtering."""
    try:
        query = select(DataFeed).order_by(desc(DataFeed.updated_at))

        if is_active is not None:
            query = query.where(DataFeed.is_active == is_active)

        if feed_type:
            query = query.where(DataFeed.feed_type == feed_type)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        feeds = result.scalars().all()

        return feeds
    except Exception as e:
        logger.error(f"Error fetching data feeds: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data feeds")


@router.get("/{feed_id}", response_model=DataFeedSchema)
async def get_data_feed(feed_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific data feed by ID."""
    try:
        result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
        feed = result.scalar_one_or_none()

        if not feed:
            raise HTTPException(status_code=404, detail="Data feed not found")

        return feed
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching data feed {feed_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data feed")


@router.post("", response_model=DataFeedSchema)
async def create_data_feed(
    feed: DataFeedCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new data feed."""
    try:
        db_feed = DataFeed(
            name=feed.name,
            source=feed.source,
            api_url=feed.api_url,
            api_key=feed.api_key,
            feed_type=feed.feed_type,
            polling_interval=feed.polling_interval,
            description=feed.description,
        )

        db.add(db_feed)
        await db.commit()
        await db.refresh(db_feed)

        logger.info(f"Data feed created with ID {db_feed.id}: {feed.name}")
        return db_feed
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating data feed: {e}")
        raise HTTPException(status_code=500, detail="Error creating data feed")


@router.put("/{feed_id}", response_model=DataFeedSchema)
async def update_data_feed(
    feed_id: int, feed_update: dict, db: AsyncSession = Depends(get_db)
):
    """Update a data feed."""
    try:
        result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
        db_feed = result.scalar_one_or_none()

        if not db_feed:
            raise HTTPException(status_code=404, detail="Data feed not found")

        # Update allowed fields
        for field, value in feed_update.items():
            if hasattr(db_feed, field) and field not in ["id", "created_at"]:
                setattr(db_feed, field, value)

        db_feed.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_feed)

        logger.info(f"Data feed {feed_id} updated")
        return db_feed
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating data feed {feed_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating data feed")


@router.put("/{feed_id}/toggle", response_model=DataFeedSchema)
async def toggle_feed_active(feed_id: int, db: AsyncSession = Depends(get_db)):
    """Toggle data feed active status."""
    try:
        result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
        db_feed = result.scalar_one_or_none()

        if not db_feed:
            raise HTTPException(status_code=404, detail="Data feed not found")

        db_feed.is_active = not db_feed.is_active
        db_feed.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_feed)

        status = "activated" if db_feed.is_active else "deactivated"
        logger.info(f"Data feed {feed_id} {status}")
        return db_feed
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error toggling data feed {feed_id}: {e}")
        raise HTTPException(status_code=500, detail="Error toggling data feed")


@router.get("/{feed_id}/data", response_model=List[RawDataPointSchema])
async def get_feed_data_points(
    feed_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get recent data points for a feed."""
    try:
        query = (
            select(RawDataPoint)
            .where(RawDataPoint.data_feed_id == feed_id)
            .order_by(desc(RawDataPoint.timestamp))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        points = result.scalars().all()

        return points
    except Exception as e:
        logger.error(f"Error fetching data points for feed {feed_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data points")


@router.post("/{feed_id}/data", response_model=RawDataPointSchema)
async def add_data_point(
    feed_id: int, value: float, metadata: dict = None, db: AsyncSession = Depends(get_db)
):
    """Add a raw data point to a feed."""
    try:
        # Verify feed exists
        result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
        feed = result.scalar_one_or_none()

        if not feed:
            raise HTTPException(status_code=404, detail="Data feed not found")

        db_point = RawDataPoint(
            data_feed_id=feed_id,
            value=value,
            metadata=metadata,
            timestamp=datetime.utcnow(),
        )

        # Update feed's last_polled
        feed.last_polled = datetime.utcnow()
        feed.last_value = {"value": value, "metadata": metadata}

        db.add(db_point)
        await db.commit()
        await db.refresh(db_point)

        logger.info(f"Data point added to feed {feed_id}: {value}")
        return db_point
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error adding data point to feed {feed_id}: {e}")
        raise HTTPException(status_code=500, detail="Error adding data point")


@router.get("/stats/feed-health", response_model=dict)
async def get_feed_health(db: AsyncSession = Depends(get_db)):
    """Get health status of all data feeds."""
    try:
        result = await db.execute(select(DataFeed))
        feeds = result.scalars().all()

        health_status = {
            "total_feeds": len(feeds),
            "active_feeds": sum(1 for f in feeds if f.is_active),
            "feeds_with_errors": sum(1 for f in feeds if f.error_count > 0),
            "feeds_with_recent_data": sum(
                1
                for f in feeds
                if f.last_polled and (datetime.utcnow() - f.last_polled).total_seconds() < 600
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return health_status
    except Exception as e:
        logger.error(f"Error getting feed health: {e}")
        raise HTTPException(status_code=500, detail="Error getting feed health")
