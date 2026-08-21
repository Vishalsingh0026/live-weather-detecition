import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.database import get_db
from backend.models import ResponsePlan, ResourceAllocation
from backend.schemas import ResponsePlan as ResponsePlanSchema, ResponsePlanCreate

logger = logging.getLogger(__name__)

router = APIRouter()


class PlanStatusUpdate(BaseModel):
    new_status: str


@router.get("", response_model=List[ResponsePlanSchema])
async def get_response_plans(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all response plans with optional filtering."""
    try:
        query = select(ResponsePlan).order_by(desc(ResponsePlan.created_at))

        if status:
            query = query.where(ResponsePlan.status == status)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        plans = result.scalars().all()

        return plans
    except Exception as e:
        logger.error(f"Error fetching response plans: {e}")
        raise HTTPException(status_code=500, detail="Error fetching response plans")


@router.get("/{plan_id}", response_model=ResponsePlanSchema)
async def get_response_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific response plan by ID."""
    try:
        result = await db.execute(
            select(ResponsePlan).where(ResponsePlan.id == plan_id)
        )
        plan = result.scalar_one_or_none()

        if not plan:
            raise HTTPException(status_code=404, detail="Response plan not found")

        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching response plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching response plan")


@router.post("", response_model=ResponsePlanSchema)
async def create_response_plan(
    plan: ResponsePlanCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new response plan."""
    try:
        # Convert schema objects to JSON-serializable dicts
        actions_data = [
            {
                "action": action.action,
                "priority": action.priority,
                "estimated_duration_hours": action.estimated_duration_hours,
                "assigned_to": action.assigned_to,
            }
            for action in plan.recommended_actions
        ]

        resources_data = [
            {
                "resource_type": resource.resource_type,
                "quantity": resource.quantity,
                "priority": resource.priority,
            }
            for resource in plan.resource_requirements
        ]

        db_plan = ResponsePlan(
            event_id=plan.event_id,
            title=plan.title,
            description=plan.description,
            recommended_actions=actions_data,
            resource_requirements=resources_data,
            priority_level=plan.priority_level,
            status="draft",
        )

        db.add(db_plan)
        await db.commit()
        await db.refresh(db_plan)

        logger.info(f"Response plan created with ID {db_plan.id}")
        return db_plan
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating response plan: {e}")
        raise HTTPException(status_code=500, detail="Error creating response plan")


@router.put("/{plan_id}/status", response_model=ResponsePlanSchema)
async def update_plan_status(
    plan_id: int,
    status_update: PlanStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update response plan status."""
    valid_statuses = ["draft", "approved", "executing", "completed"]
    new_status = status_update.new_status
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        result = await db.execute(
            select(ResponsePlan).where(ResponsePlan.id == plan_id)
        )
        db_plan = result.scalar_one_or_none()

        if not db_plan:
            raise HTTPException(status_code=404, detail="Response plan not found")

        status_order = ["draft", "approved", "executing", "completed"]
        current_index = status_order.index(db_plan.status)
        requested_index = status_order.index(new_status)
        if requested_index != current_index + 1:
            raise HTTPException(
                status_code=409,
                detail=f"Plan can only move from {db_plan.status} to {status_order[current_index + 1] if current_index + 1 < len(status_order) else 'completed'}",
            )

        db_plan.status = new_status
        db_plan.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_plan)

        logger.info(f"Response plan {plan_id} status updated to {new_status}")
        return db_plan
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating response plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating response plan")


@router.get("/event/{event_id}", response_model=Optional[ResponsePlanSchema])
async def get_plan_by_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Get response plan for a specific event."""
    try:
        result = await db.execute(
            select(ResponsePlan).where(ResponsePlan.event_id == event_id)
        )
        plan = result.scalar_one_or_none()

        return plan
    except Exception as e:
        logger.error(f"Error fetching response plan for event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching response plan")
