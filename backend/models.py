from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from backend.database import Base


class EventType(str, enum.Enum):
    EXTREME_RAINFALL = "extreme_rainfall"
    FLOOD_RISK = "flood_risk"
    EXTREME_HEAT = "extreme_heat"
    WATER_SHORTAGE = "water_shortage"
    SEVERE_WEATHER = "severe_weather"
    EARTHQUAKE = "earthquake"
    OTHER = "other"


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    events = relationship("Event", back_populates="created_by")
    alerts = relationship("Alert", back_populates="created_by")


class DataFeed(Base):
    __tablename__ = "data_feeds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False, unique=True)
    api_url = Column(String(2048), nullable=False)
    api_key = Column(String(512), nullable=True)
    feed_type = Column(String(100), nullable=False)  # weather, earthquake, flood, etc.
    is_active = Column(Boolean, default=True)
    polling_interval = Column(Integer, default=300)  # seconds
    last_polled = Column(DateTime, nullable=True)
    last_value = Column(JSON, nullable=True)
    error_count = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    raw_data_points = relationship("RawDataPoint", back_populates="data_feed")


class RawDataPoint(Base):
    __tablename__ = "raw_data_points"

    id = Column(Integer, primary_key=True, index=True)
    data_feed_id = Column(Integer, ForeignKey("data_feeds.id"), nullable=False)
    value = Column(Float, nullable=False)
    metadata_json = Column(JSON, nullable=True)  # Store latitude, longitude, etc.
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    data_feed = relationship("DataFeed", back_populates="raw_data_points")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    location = Column(String(512), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(Integer, default=50)  # 0-100 risk score
    confidence = Column(Float, default=0.5)  # 0-1.0 confidence
    description = Column(Text, nullable=True)
    data_source = Column(String(512), nullable=False)
    raw_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("User", back_populates="events")
    alerts = relationship("Alert", back_populates="event")
    response_plan = relationship("ResponsePlan", uselist=False, back_populates="event")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    title = Column(String(512), nullable=False)
    message = Column(Text, nullable=False)
    recipient_emails = Column(JSON, nullable=True)  # Array of emails
    is_sent = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="alerts")
    created_by = relationship("User", back_populates="alerts")


class ResponsePlan(Base):
    __tablename__ = "response_plans"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, unique=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    recommended_actions = Column(JSON, nullable=False)  # Array of actions
    resource_requirements = Column(JSON, nullable=False)  # Resource needs
    estimated_impact = Column(JSON, nullable=True)
    priority_level = Column(Integer, default=50)  # 1-100
    status = Column(String(50), default="draft")  # draft, approved, executing, completed
    generated_by = Column(String(100), default="ai_engine")  # Which AI/system generated this
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="response_plan")
    resource_allocations = relationship("ResourceAllocation", back_populates="response_plan")


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id = Column(Integer, primary_key=True, index=True)
    response_plan_id = Column(Integer, ForeignKey("response_plans.id"), nullable=False)
    resource_type = Column(String(100), nullable=False)  # personnel, equipment, vehicles, etc.
    quantity = Column(Integer, nullable=False)
    location = Column(String(512), nullable=False)
    status = Column(String(50), default="pending")  # pending, allocated, deployed, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    response_plan = relationship("ResponsePlan", back_populates="resource_allocations")


class AnomalyScore(Base):
    __tablename__ = "anomaly_scores"

    id = Column(Integer, primary_key=True, index=True)
    data_feed_id = Column(Integer, ForeignKey("data_feeds.id"), nullable=False)
    anomaly_score = Column(Float, nullable=False)  # 0-1.0
    is_anomalous = Column(Boolean, default=False)
    method = Column(String(100), nullable=False)  # Method used (isolation_forest, etc.)
    threshold = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    data_feed = relationship("DataFeed")
