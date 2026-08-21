from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.models import EventType, AlertSeverity


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Data Feed Schemas
class DataFeedBase(BaseModel):
    name: str
    source: str
    api_url: str
    feed_type: str
    polling_interval: int = 300
    description: Optional[str] = None


class DataFeedCreate(DataFeedBase):
    api_key: Optional[str] = None


class DataFeed(DataFeedBase):
    id: int
    is_active: bool
    last_polled: Optional[datetime]
    last_value: Optional[Dict[str, Any]]
    error_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Raw Data Point Schemas
class RawDataPointBase(BaseModel):
    value: float
    metadata: Optional[Dict[str, Any]] = None


class RawDataPointCreate(RawDataPointBase):
    data_feed_id: int
    timestamp: Optional[datetime] = None


class RawDataPoint(RawDataPointBase):
    id: int
    data_feed_id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Event Schemas
class EventBase(BaseModel):
    event_type: EventType
    location: str
    latitude: float
    longitude: float
    severity: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    description: Optional[str] = None
    data_source: str


class EventCreate(EventBase):
    raw_data: Optional[Dict[str, Any]] = None


class Event(EventBase):
    id: int
    is_active: bool
    detected_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    title: str
    message: str
    severity: AlertSeverity = AlertSeverity.MEDIUM
    recipient_emails: Optional[List[str]] = None


class AlertCreate(AlertBase):
    event_id: int


class Alert(AlertBase):
    id: int
    event_id: int
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Response Plan Schemas
class ResourceRequirement(BaseModel):
    resource_type: str
    quantity: int
    priority: str = "medium"


class RecommendedAction(BaseModel):
    action: str
    priority: int
    estimated_duration_hours: Optional[int] = None
    assigned_to: Optional[str] = None


class ResponsePlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    recommended_actions: List[RecommendedAction]
    resource_requirements: List[ResourceRequirement]
    priority_level: int = Field(ge=1, le=100)


class ResponsePlanCreate(ResponsePlanBase):
    event_id: int


class ResponsePlan(ResponsePlanBase):
    id: int
    event_id: int
    status: str
    generated_by: str
    estimated_impact: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Resource Allocation Schemas
class ResourceAllocationBase(BaseModel):
    resource_type: str
    quantity: int
    location: str


class ResourceAllocationCreate(ResourceAllocationBase):
    response_plan_id: int


class ResourceAllocation(ResourceAllocationBase):
    id: int
    response_plan_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Anomaly Score Schemas
class AnomalyScoreResponse(BaseModel):
    data_feed_id: int
    anomaly_score: float
    is_anomalous: bool
    method: str
    threshold: float
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard/Live Metrics Schemas
class LiveMetrics(BaseModel):
    total_active_events: int
    critical_alerts: int
    high_severity_count: int
    average_risk_score: float
    last_updated: datetime


class DashboardStats(BaseModel):
    live_metrics: LiveMetrics
    top_events: List[Event]
    recent_alerts: List[Alert]
    active_response_plans: List[ResponsePlan]


# Real-time WebSocket Message Schemas
class WebSocketMessage(BaseModel):
    type: str  # event_detected, alert_triggered, status_update, etc.
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "backend"
