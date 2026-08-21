import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.models import (
    Event,
    EventType,
    DataFeed,
    RawDataPoint,
    Alert,
    AlertSeverity,
    ResponsePlan,
)
from backend.services.api_client import api_client
from backend.services.anomaly_detection import anomaly_detector
from backend.services.risk_assessment import risk_assessor
from backend.services.ai_planner import ai_planner
from backend.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class DataStreamProcessor:
    """Orchestrates real-time data ingestion, anomaly detection, and event creation."""

    def __init__(self):
        self.is_running = False
        self.polling_tasks: Dict[str, asyncio.Task] = {}
        self.seen_earthquakes = set()

    async def start(self):
        """Start the data stream processor."""
        logger.info("Starting Data Stream Processor")
        self.is_running = True
        await api_client.initialize()

        # Start polling tasks for each data feed
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DataFeed).where(DataFeed.is_active.is_(True))
            )
            feeds = result.scalars().all()

        for feed in feeds:
            if feed.feed_type.lower() in {"weather", "rainfall", "flood"}:
                task_name = f"weather:{feed.id}"
                self.polling_tasks[task_name] = asyncio.create_task(
                    self._poll_weather_feed(feed.id, feed.polling_interval or 300),
                    name=task_name,
                )
            elif feed.feed_type.lower() in {"earthquake", "seismic"}:
                task_name = f"earthquake:{feed.id}"
                self.polling_tasks[task_name] = asyncio.create_task(
                    self._poll_earthquake_feed(feed.id, feed.polling_interval or 300),
                    name=task_name,
                )

        logger.info("Started %d data feed polling tasks", len(self.polling_tasks))

    async def stop(self):
        """Stop the data stream processor."""
        logger.info("Stopping Data Stream Processor")
        self.is_running = False
        await api_client.close()

        # Cancel all polling tasks
        for task_id, task in self.polling_tasks.items():
            task.cancel()
            logger.info(f"Cancelled polling task {task_id}")

        if self.polling_tasks:
            await asyncio.gather(*self.polling_tasks.values(), return_exceptions=True)

        self.polling_tasks.clear()

    async def _poll_weather_feed(self, feed_id: int, interval: int):
        """Poll a weather feed at its configured interval."""
        while self.is_running:
            try:
                result = await self.process_weather_data(
                    settings.default_latitude,
                    settings.default_longitude,
                    settings.default_country,
                )
                await self._persist_detection_result(feed_id, result)
                await self._mark_feed_polled(feed_id, result)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Weather feed %s polling failed", feed_id)
                await self._mark_feed_polled(feed_id, None, failed=True)
            await asyncio.sleep(interval)

    async def _poll_earthquake_feed(self, feed_id: int, interval: int):
        """Poll the USGS earthquake feed at its configured interval."""
        while self.is_running:
            try:
                result = await self.process_earthquake_data()
                new_events = [
                    event for event in result.get("events_detected", [])
                    if event["raw_data"].get("event_id") not in self.seen_earthquakes
                ]
                self.seen_earthquakes.update(
                    event["raw_data"].get("event_id")
                    for event in new_events
                    if event["raw_data"].get("event_id")
                )
                result["events_detected"] = new_events
                await self._persist_detection_result(feed_id, result)
                await self._mark_feed_polled(feed_id, result)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Earthquake feed %s polling failed", feed_id)
                await self._mark_feed_polled(feed_id, None, failed=True)
            await asyncio.sleep(interval)

    async def _persist_detection_result(self, feed_id: int, result: Dict[str, Any]):
        """Persist each newly detected event with its alert and response plan."""
        for event_data in result.get("events_detected", []):
            async with AsyncSessionLocal() as session:
                try:
                    event = await self.save_event_to_db(event_data, session)
                    if event.severity >= settings.alert_threshold:
                        await self.create_alert_for_event(event, session)
                    plan_data = await self.generate_response_plan_for_event(event, session)
                    if "error" not in plan_data:
                        session.add(
                            ResponsePlan(
                                event_id=event.id,
                                title=plan_data["title"],
                                description=plan_data.get("description"),
                                recommended_actions=plan_data["recommended_actions"],
                                resource_requirements=plan_data["resource_requirements"],
                                estimated_impact=plan_data.get("estimated_impact"),
                                priority_level=plan_data["priority_level"],
                                status="draft",
                            )
                        )
                    await session.commit()
                except Exception:
                    await session.rollback()
                    logger.exception("Failed to persist detected event")

    async def _mark_feed_polled(
        self, feed_id: int, result: Dict[str, Any] | None, failed: bool = False
    ):
        async with AsyncSessionLocal() as session:
            feed = await session.get(DataFeed, feed_id)
            if feed:
                feed.last_polled = datetime.utcnow()
                feed.error_count = (feed.error_count or 0) + (1 if failed else 0)
                if result and result.get("data"):
                    feed.last_value = result["data"]
                await session.commit()

    async def process_weather_data(
        self, latitude: float, longitude: float, location: str
    ) -> Dict[str, Any]:
        """Process real-time weather data and detect anomalies."""
        logger.info(f"Processing weather data for {location}")

        try:
            response = await api_client.fetch_weather_data(latitude, longitude)

            if not response.get("success"):
                logger.error(f"Failed to fetch weather data: {response.get('error')}")
                return {"success": False, "error": response.get("error")}

            weather_data = response.get("data", {})
            current = weather_data.get("current", {})

            # Extract key metrics
            temperature = current.get("temperature_2m", 0)
            humidity = current.get("relative_humidity_2m", 0)
            precipitation = current.get("precipitation", 0)
            wind_speed = current.get("wind_speed_10m", 0)

            events_detected = []

            # Detect extreme rainfall
            if precipitation > 20:  # mm threshold
                is_anomalous, anomaly_score, _ = anomaly_detector.detect_anomaly(
                    feed_id=1, value=precipitation
                )
                if is_anomalous or precipitation > 50:
                    risk_score, risk_level, reasoning = risk_assessor.assess_risk(
                        "extreme_rainfall",
                        anomaly_score,
                        0.8,
                        {
                            "location": location,
                            "location_type": "urban",
                            "precipitation": precipitation,
                        },
                    )
                    events_detected.append(
                        {
                            "type": EventType.EXTREME_RAINFALL,
                            "severity": risk_score,
                            "confidence": 0.8,
                            "description": f"Heavy rainfall: {precipitation}mm detected",
                            "raw_data": {
                                "precipitation_mm": precipitation,
                                "humidity": humidity,
                                "wind_speed": wind_speed,
                            },
                        }
                    )
                    logger.info(
                        f"Extreme rainfall detected: {precipitation}mm at {location}"
                    )

            # Detect extreme heat
            if temperature > 40:  # Celsius
                is_anomalous, anomaly_score, _ = anomaly_detector.detect_anomaly(
                    feed_id=2, value=temperature
                )
                if is_anomalous or temperature > 45:
                    risk_score, risk_level, reasoning = risk_assessor.assess_risk(
                        "extreme_heat",
                        anomaly_score,
                        0.85,
                        {
                            "location": location,
                            "location_type": "urban",
                            "temperature": temperature,
                        },
                    )
                    events_detected.append(
                        {
                            "type": EventType.EXTREME_HEAT,
                            "severity": risk_score,
                            "confidence": 0.85,
                            "description": f"Extreme heat detected: {temperature}°C",
                            "raw_data": {
                                "temperature_celsius": temperature,
                                "humidity": humidity,
                            },
                        }
                    )
                    logger.info(f"Extreme heat detected: {temperature}°C at {location}")

            # Detect severe weather (wind speed)
            if wind_speed > 40:  # km/h
                is_anomalous, anomaly_score, _ = anomaly_detector.detect_anomaly(
                    feed_id=3, value=wind_speed
                )
                if is_anomalous or wind_speed > 60:
                    risk_score, risk_level, reasoning = risk_assessor.assess_risk(
                        "severe_weather",
                        anomaly_score,
                        0.8,
                        {
                            "location": location,
                            "location_type": "urban",
                            "wind_speed": wind_speed,
                        },
                    )
                    events_detected.append(
                        {
                            "type": EventType.SEVERE_WEATHER,
                            "severity": risk_score,
                            "confidence": 0.8,
                            "description": f"Severe winds detected: {wind_speed}km/h",
                            "raw_data": {
                                "wind_speed_kmh": wind_speed,
                                "precipitation": precipitation,
                            },
                        }
                    )
                    logger.info(f"Severe weather detected: {wind_speed}km/h at {location}")

            return {"success": True, "events_detected": events_detected, "data": current}

        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return {"success": False, "error": str(e)}

    async def process_earthquake_data(self) -> Dict[str, Any]:
        """Process real-time earthquake data from USGS."""
        logger.info("Processing earthquake data")

        try:
            response = await api_client.fetch_earthquake_data()

            if not response.get("success"):
                logger.error(f"Failed to fetch earthquake data: {response.get('error')}")
                return {"success": False, "error": response.get("error")}

            earthquake_data = response.get("data", {})
            features = earthquake_data.get("features", [])
            events_detected = []

            # Process significant earthquakes in India region
            for feature in features:
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                coordinates = geometry.get("coordinates", [0, 0, 0])

                magnitude = properties.get("mag", 0)
                place = properties.get("place", "Unknown")
                latitude = coordinates[1]
                longitude = coordinates[0]

                # Check if in India region (approximately)
                if 8 < latitude < 37 and 68 < longitude < 97 and magnitude > 4.0:
                    risk_score, risk_level, _ = risk_assessor.assess_risk(
                        "earthquake",
                        min(1.0, magnitude / 8),
                        0.9,
                        {
                            "location": place,
                            "location_type": "seismic",
                            "magnitude": magnitude,
                        },
                    )

                    events_detected.append(
                        {
                            "type": EventType.EARTHQUAKE,
                            "severity": risk_score,
                            "confidence": 0.9,
                            "location": place,
                            "latitude": latitude,
                            "longitude": longitude,
                            "description": f"Earthquake magnitude {magnitude} detected",
                            "raw_data": {
                                "event_id": feature.get("id"),
                                "magnitude": magnitude,
                                "latitude": latitude,
                                "longitude": longitude,
                                "place": place,
                            },
                        }
                    )
                    logger.warning(
                        f"Earthquake detected: Magnitude {magnitude} at {place}"
                    )

            return {"success": True, "events_detected": events_detected}

        except Exception as e:
            logger.error(f"Error processing earthquake data: {e}")
            return {"success": False, "error": str(e)}

    async def save_event_to_db(
        self, event_data: Dict[str, Any], session: AsyncSession
    ) -> Event:
        """Save detected event to database."""
        try:
            db_event = Event(
                event_type=event_data.get("type", EventType.OTHER),
                location=event_data.get("location", "Unknown"),
                latitude=event_data.get("latitude", 0.0),
                longitude=event_data.get("longitude", 0.0),
                severity=event_data.get("severity", 50),
                confidence=event_data.get("confidence", 0.5),
                description=event_data.get("description", ""),
                data_source="automatic_detection",
                raw_data=event_data.get("raw_data", {}),
                detected_at=datetime.utcnow(),
            )

            session.add(db_event)
            await session.flush()

            logger.info(f"Event saved to DB with ID {db_event.id}")
            return db_event

        except Exception as e:
            logger.error(f"Error saving event to database: {e}")
            raise

    async def create_alert_for_event(
        self, event: Event, session: AsyncSession
    ) -> Alert:
        """Create alert for a detected event."""
        try:
            alert = Alert(
                event_id=event.id,
                severity=AlertSeverity.CRITICAL
                if event.severity >= 85
                else AlertSeverity.HIGH
                if event.severity >= 70
                else AlertSeverity.MEDIUM,
                title=f"Disaster Alert: {event.event_type.value.replace('_', ' ').title()}",
                message=f"A {event.event_type.value.replace('_', ' ')} event has been detected in {event.location} "
                f"with severity {event.severity}/100.",
                recipient_emails=["admin@bharatresilience.ai"],
            )

            session.add(alert)
            await session.flush()

            logger.info(f"Alert created for event {event.id}")
            return alert

        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise

    async def generate_response_plan_for_event(
        self, event: Event, session: AsyncSession
    ) -> Dict[str, Any]:
        """Generate AI response plan for event."""
        try:
            plan_data = ai_planner.generate_response_plan(
                event_id=event.id,
                event_type=event.event_type.value,
                location=event.location,
                severity=event.severity,
                confidence=event.confidence,
                raw_data=event.raw_data or {},
            )

            logger.info(f"Response plan generated for event {event.id}")
            return plan_data

        except Exception as e:
            logger.error(f"Error generating response plan: {e}")
            return {"error": str(e)}


data_processor = DataStreamProcessor()
