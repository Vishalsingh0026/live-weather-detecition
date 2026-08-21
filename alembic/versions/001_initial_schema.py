"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2024-01-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all database tables."""
    # Create enum types
    event_type_enum = postgresql.ENUM(
        'extreme_rainfall', 'flood_risk', 'extreme_heat',
        'water_shortage', 'severe_weather', 'earthquake', 'custom',
        name='eventtype',
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)

    alert_severity_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical', name='alertseverity'
    )
    alert_severity_enum.create(op.get_bind(), checkfirst=True)

    plan_status_enum = postgresql.ENUM(
        'draft', 'approved', 'executing', 'completed', name='planstatus'
    )
    plan_status_enum.create(op.get_bind(), checkfirst=True)

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Data feeds table
    op.create_table(
        'data_feeds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('api_url', sa.String(length=500), nullable=False),
        sa.Column('feed_type', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('polling_interval_seconds', sa.Integer(), nullable=True),
        sa.Column('last_polled', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_value', sa.Float(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_data_feeds_id'), 'data_feeds', ['id'], unique=False)

    # Events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', postgresql.ENUM(name='eventtype', create_type=False), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('severity', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_source', sa.String(length=255), nullable=False),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_detected_at'), 'events', ['detected_at'], unique=False)

    # Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('severity', postgresql.ENUM(name='alertseverity', create_type=False), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('recipient_emails', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_sent', sa.Boolean(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_event_id'), 'alerts', ['event_id'], unique=False)

    # Response plans table
    op.create_table(
        'response_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('recommended_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('resource_requirements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', postgresql.ENUM(name='planstatus', create_type=False), nullable=False),
        sa.Column('priority_level', sa.Integer(), nullable=True),
        sa.Column('estimated_impact', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_response_plans_id'), 'response_plans', ['id'], unique=False)
    op.create_index(op.f('ix_response_plans_event_id'), 'response_plans', ['event_id'], unique=False)

    # Resource allocations table
    op.create_table(
        'resource_allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('response_plan_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('allocated_quantity', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['response_plan_id'], ['response_plans.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_resource_allocations_id'), 'resource_allocations', ['id'], unique=False)

    # Raw data points table
    op.create_table(
        'raw_data_points',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['feed_id'], ['data_feeds.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_raw_data_points_id'), 'raw_data_points', ['id'], unique=False)
    op.create_index(op.f('ix_raw_data_points_feed_id'), 'raw_data_points', ['feed_id'], unique=False)
    op.create_index(op.f('ix_raw_data_points_timestamp'), 'raw_data_points', ['timestamp'], unique=False)

    # Anomaly scores table
    op.create_table(
        'anomaly_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('is_anomaly', sa.Boolean(), nullable=False),
        sa.Column('detection_method', sa.String(length=100), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.ForeignKeyConstraint(['feed_id'], ['data_feeds.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_anomaly_scores_id'), 'anomaly_scores', ['id'], unique=False)
    op.create_index(op.f('ix_anomaly_scores_event_id'), 'anomaly_scores', ['event_id'], unique=False)
    op.create_index(op.f('ix_anomaly_scores_feed_id'), 'anomaly_scores', ['feed_id'], unique=False)


def downgrade() -> None:
    """Drop all database tables."""
    op.drop_table('anomaly_scores')
    op.drop_table('raw_data_points')
    op.drop_table('resource_allocations')
    op.drop_table('response_plans')
    op.drop_table('alerts')
    op.drop_table('events')
    op.drop_table('data_feeds')
    op.drop_table('users')

    op.execute('DROP TYPE IF EXISTS planstatus')
    op.execute('DROP TYPE IF EXISTS alertseverity')
    op.execute('DROP TYPE IF EXISTS eventtype')
