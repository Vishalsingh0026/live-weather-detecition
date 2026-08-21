import logging
from typing import Dict, Any, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessmentService:
    """Service for assessing risk based on anomaly data and thresholds."""

    def __init__(self):
        # Risk thresholds for different event types
        self.risk_thresholds = {
            "extreme_rainfall": {"warning": 50, "alert": 70, "critical": 85},
            "flood_risk": {"warning": 45, "alert": 65, "critical": 80},
            "extreme_heat": {"warning": 55, "alert": 75, "critical": 90},
            "water_shortage": {"warning": 40, "alert": 60, "critical": 75},
            "severe_weather": {"warning": 50, "alert": 70, "critical": 85},
            "earthquake": {"warning": 40, "alert": 60, "critical": 80},
        }

        # Location-specific multipliers (can be extended)
        self.location_risk_multipliers = {
            "flood_prone": 1.3,
            "drought_prone": 1.2,
            "seismic": 1.4,
            "urban": 1.1,
            "rural": 0.9,
        }

    def assess_risk(
        self,
        event_type: str,
        anomaly_score: float,
        confidence: float,
        metadata: Dict[str, Any],
    ) -> Tuple[int, RiskLevel, str]:
        """
        Assess risk for an event.

        Args:
            event_type: Type of event (e.g., 'extreme_rainfall')
            anomaly_score: Anomaly detection score (0-1)
            confidence: Confidence level (0-1)
            metadata: Additional context (location characteristics, etc.)

        Returns:
            Tuple of (risk_score, risk_level, reasoning)
        """
        # Base risk score from anomaly
        base_score = anomaly_score * 100

        # Apply confidence multiplier
        risk_score = base_score * confidence

        # Apply location multipliers
        location_type = metadata.get("location_type", "urban")
        if location_type in self.location_risk_multipliers:
            risk_score *= self.location_risk_multipliers[location_type]

        # Clamp to 0-100
        risk_score = min(100, max(0, risk_score))

        # Determine risk level
        risk_level = self._get_risk_level(event_type, risk_score)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            event_type, risk_score, confidence, metadata
        )

        logger.info(
            f"Risk assessment for {event_type}: score={risk_score:.1f}, level={risk_level}"
        )

        return int(risk_score), risk_level, reasoning

    def _get_risk_level(self, event_type: str, risk_score: float) -> RiskLevel:
        """Determine risk level based on score and event type."""
        thresholds = self.risk_thresholds.get(
            event_type, {"warning": 50, "alert": 70, "critical": 85}
        )

        if risk_score >= thresholds["critical"]:
            return RiskLevel.CRITICAL
        elif risk_score >= thresholds["alert"]:
            return RiskLevel.HIGH
        elif risk_score >= thresholds["warning"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_reasoning(
        self,
        event_type: str,
        risk_score: float,
        confidence: float,
        metadata: Dict[str, Any],
    ) -> str:
        """Generate human-readable risk assessment reasoning."""
        location = metadata.get("location", "Unknown")
        location_type = metadata.get("location_type", "urban")

        reasoning = f"Event: {event_type.replace('_', ' ').title()} detected in {location}. "
        reasoning += f"Risk Score: {risk_score:.0f}/100 | Confidence: {confidence*100:.0f}%. "
        reasoning += f"Location type: {location_type}. "

        if risk_score >= 85:
            reasoning += "IMMEDIATE ACTION REQUIRED. Critical threat level."
        elif risk_score >= 70:
            reasoning += "Alert conditions detected. Prepare emergency response."
        elif risk_score >= 50:
            reasoning += "Monitor situation closely. Preparedness measures recommended."
        else:
            reasoning += "Low risk. Continue routine monitoring."

        return reasoning

    def multi_event_risk(self, events: list) -> Dict[str, Any]:
        """Assess combined risk from multiple simultaneous events."""
        if not events:
            return {"combined_risk": 0, "level": RiskLevel.LOW, "event_count": 0}

        total_risk = 0
        event_count = len(events)
        risk_levels = []

        for event in events:
            risk_score, risk_level, _ = self.assess_risk(
                event.get("event_type", "other"),
                event.get("anomaly_score", 0.5),
                event.get("confidence", 0.5),
                event.get("metadata", {}),
            )
            total_risk += risk_score
            risk_levels.append(risk_level)

        # Average with multiplier for multiple events (more events = higher combined risk)
        combined_risk = (total_risk / event_count) * (1 + (event_count - 1) * 0.1)
        combined_risk = min(100, combined_risk)

        # Overall level is the highest among individual events
        max_level = RiskLevel.CRITICAL
        for level in risk_levels:
            if level == RiskLevel.CRITICAL:
                break
            elif level == RiskLevel.HIGH:
                max_level = RiskLevel.HIGH
            elif level == RiskLevel.MEDIUM and max_level != RiskLevel.HIGH:
                max_level = RiskLevel.MEDIUM
            elif level == RiskLevel.LOW and max_level == RiskLevel.LOW:
                max_level = RiskLevel.LOW

        return {
            "combined_risk": int(combined_risk),
            "level": max_level,
            "event_count": event_count,
            "event_types": [e.get("event_type", "other") for e in events],
            "average_confidence": sum(e.get("confidence", 0) for e in events)
            / event_count,
        }


risk_assessor = RiskAssessmentService()
