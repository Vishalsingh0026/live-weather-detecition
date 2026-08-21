import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from backend.schemas import RecommendedAction, ResourceRequirement

logger = logging.getLogger(__name__)


class AIPlanningEngine:
    """Service for generating AI-based response plans for disasters."""

    def __init__(self):
        self.action_templates = self._initialize_action_templates()
        self.resource_templates = self._initialize_resource_templates()

    def _initialize_action_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize recommended actions for different event types."""
        return {
            "extreme_rainfall": [
                {
                    "action": "Issue public alert for heavy rainfall warning",
                    "priority": 1,
                    "duration_hours": 2,
                    "assigned_to": "emergency_management",
                },
                {
                    "action": "Deploy drainage maintenance teams to critical areas",
                    "priority": 2,
                    "duration_hours": 4,
                    "assigned_to": "municipal_services",
                },
                {
                    "action": "Prepare evacuation routes from flood-prone areas",
                    "priority": 2,
                    "duration_hours": 3,
                    "assigned_to": "disaster_management",
                },
                {
                    "action": "Position rescue teams at high-risk zones",
                    "priority": 3,
                    "duration_hours": 8,
                    "assigned_to": "rescue_services",
                },
            ],
            "flood_risk": [
                {
                    "action": "Activate flood early warning system",
                    "priority": 1,
                    "duration_hours": 1,
                    "assigned_to": "emergency_management",
                },
                {
                    "action": "Open emergency shelters in vulnerable areas",
                    "priority": 1,
                    "duration_hours": 6,
                    "assigned_to": "social_services",
                },
                {
                    "action": "Mobilize rescue boats and equipment",
                    "priority": 2,
                    "duration_hours": 4,
                    "assigned_to": "rescue_services",
                },
                {
                    "action": "Set up medical camps for injury treatment",
                    "priority": 2,
                    "duration_hours": 8,
                    "assigned_to": "health_services",
                },
                {
                    "action": "Distribute drinking water and food supplies",
                    "priority": 3,
                    "duration_hours": 12,
                    "assigned_to": "logistics",
                },
            ],
            "extreme_heat": [
                {
                    "action": "Activate heat alert system and public warnings",
                    "priority": 1,
                    "duration_hours": 2,
                    "assigned_to": "emergency_management",
                },
                {
                    "action": "Open cooling centers in public spaces",
                    "priority": 1,
                    "duration_hours": 12,
                    "assigned_to": "municipal_services",
                },
                {
                    "action": "Distribute water and electrolyte supplies",
                    "priority": 2,
                    "duration_hours": 8,
                    "assigned_to": "health_services",
                },
                {
                    "action": "Monitor vulnerable populations (elderly, homeless)",
                    "priority": 2,
                    "duration_hours": 24,
                    "assigned_to": "social_services",
                },
                {
                    "action": "Increase healthcare facility capacity",
                    "priority": 3,
                    "duration_hours": 12,
                    "assigned_to": "health_services",
                },
            ],
            "water_shortage": [
                {
                    "action": "Implement water rationing schedule",
                    "priority": 1,
                    "duration_hours": 4,
                    "assigned_to": "municipal_services",
                },
                {
                    "action": "Distribute emergency drinking water supplies",
                    "priority": 1,
                    "duration_hours": 8,
                    "assigned_to": "logistics",
                },
                {
                    "action": "Activate groundwater extraction contingency",
                    "priority": 2,
                    "duration_hours": 6,
                    "assigned_to": "water_department",
                },
                {
                    "action": "Public awareness campaign on water conservation",
                    "priority": 2,
                    "duration_hours": 2,
                    "assigned_to": "emergency_management",
                },
            ],
            "severe_weather": [
                {
                    "action": "Issue severe weather warning (wind/storms)",
                    "priority": 1,
                    "duration_hours": 2,
                    "assigned_to": "emergency_management",
                },
                {
                    "action": "Clear roads and secure loose structures",
                    "priority": 1,
                    "duration_hours": 3,
                    "assigned_to": "municipal_services",
                },
                {
                    "action": "Position power restoration crews",
                    "priority": 2,
                    "duration_hours": 6,
                    "assigned_to": "utilities",
                },
                {
                    "action": "Establish relief camps for affected residents",
                    "priority": 2,
                    "duration_hours": 12,
                    "assigned_to": "social_services",
                },
            ],
            "earthquake": [
                {
                    "action": "Activate emergency response protocol",
                    "priority": 1,
                    "duration_hours": 1,
                    "assigned_to": "emergency_management",
                },
                {
                    "action": "Deploy urban search and rescue teams",
                    "priority": 1,
                    "duration_hours": 24,
                    "assigned_to": "rescue_services",
                },
                {
                    "action": "Establish medical emergency centers",
                    "priority": 1,
                    "duration_hours": 24,
                    "assigned_to": "health_services",
                },
                {
                    "action": "Assess structural damage to buildings",
                    "priority": 2,
                    "duration_hours": 12,
                    "assigned_to": "engineering_services",
                },
                {
                    "action": "Activate shelter and relief operations",
                    "priority": 2,
                    "duration_hours": 48,
                    "assigned_to": "social_services",
                },
            ],
        }

    def _initialize_resource_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize resource requirements for different event types."""
        return {
            "extreme_rainfall": [
                {"resource_type": "personnel", "quantity": 50, "priority": "high"},
                {"resource_type": "pumps", "quantity": 20, "priority": "high"},
                {"resource_type": "boats", "quantity": 10, "priority": "medium"},
                {"resource_type": "medical_staff", "quantity": 20, "priority": "medium"},
                {"resource_type": "sandbags", "quantity": 10000, "priority": "high"},
            ],
            "flood_risk": [
                {"resource_type": "personnel", "quantity": 100, "priority": "high"},
                {"resource_type": "rescue_boats", "quantity": 30, "priority": "high"},
                {"resource_type": "medical_teams", "quantity": 15, "priority": "high"},
                {"resource_type": "shelter_capacity", "quantity": 5000, "priority": "high"},
                {"resource_type": "food_rations", "quantity": 10000, "priority": "medium"},
                {"resource_type": "water_tankers", "quantity": 20, "priority": "high"},
            ],
            "extreme_heat": [
                {"resource_type": "cooling_centers", "quantity": 50, "priority": "high"},
                {"resource_type": "water_supplies_liters", "quantity": 100000, "priority": "high"},
                {"resource_type": "medical_staff", "quantity": 30, "priority": "high"},
                {"resource_type": "ambulances", "quantity": 15, "priority": "high"},
                {"resource_type": "nurses", "quantity": 50, "priority": "medium"},
            ],
            "water_shortage": [
                {"resource_type": "water_tankers", "quantity": 50, "priority": "high"},
                {"resource_type": "drinking_water_liters", "quantity": 500000, "priority": "high"},
                {"resource_type": "personnel", "quantity": 30, "priority": "medium"},
                {"resource_type": "distribution_centers", "quantity": 20, "priority": "high"},
            ],
            "severe_weather": [
                {"resource_type": "personnel", "quantity": 60, "priority": "high"},
                {"resource_type": "power_restoration_crews", "quantity": 20, "priority": "high"},
                {"resource_type": "vehicles", "quantity": 50, "priority": "medium"},
                {"resource_type": "shelter_capacity", "quantity": 2000, "priority": "medium"},
            ],
            "earthquake": [
                {"resource_type": "rescue_teams", "quantity": 100, "priority": "critical"},
                {"resource_type": "search_dogs", "quantity": 20, "priority": "high"},
                {"resource_type": "medical_teams", "quantity": 50, "priority": "critical"},
                {"resource_type": "shelter_capacity", "quantity": 10000, "priority": "high"},
                {"resource_type": "engineers", "quantity": 30, "priority": "high"},
                {"resource_type": "vehicles", "quantity": 100, "priority": "high"},
            ],
        }

    def generate_response_plan(
        self,
        event_id: int,
        event_type: str,
        location: str,
        severity: int,
        confidence: float,
        raw_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI response plan for an event.

        Args:
            event_id: ID of the detected event
            event_type: Type of disaster
            location: Geographic location affected
            severity: Risk severity (0-100)
            confidence: Detection confidence (0-1)
            raw_data: Raw sensor/API data

        Returns:
            Response plan with actions and resource requirements
        """
        logger.info(f"Generating response plan for event {event_id} ({event_type})")

        # Get template actions and scale them based on severity
        actions = self._get_scaled_actions(event_type, severity)
        resources = self._get_scaled_resources(event_type, severity)

        # Calculate priority level
        priority_level = min(100, max(1, severity + (confidence * 20)))

        plan = {
            "title": f"Response Plan: {event_type.replace('_', ' ').title()} in {location}",
            "description": f"Automated disaster response plan generated at {datetime.utcnow().isoformat()}. "
            f"Severity: {severity}/100, Confidence: {confidence*100:.0f}%",
            "recommended_actions": actions,
            "resource_requirements": resources,
            "estimated_impact": {
                "severity": severity,
                "confidence": confidence,
                "estimated_affected_population": self._estimate_affected_population(
                    event_type, severity, raw_data
                ),
                "estimated_damage_cost": self._estimate_damage_cost(
                    event_type, severity, raw_data
                ),
            },
            "priority_level": int(priority_level),
            "generated_at": datetime.utcnow().isoformat(),
            "status": "draft",
        }

        return plan

    def _get_scaled_actions(
        self, event_type: str, severity: int
    ) -> List[Dict[str, Any]]:
        """Get actions scaled based on severity."""
        base_actions = self.action_templates.get(event_type, [])

        scaled_actions = []
        for action in base_actions:
            # Include all high-priority actions; scale duration based on severity
            duration_multiplier = 0.5 + (severity / 100) * 1.5
            scaled_action = {
                "action": action["action"],
                "priority": action["priority"],
                "estimated_duration_hours": int(
                    action["duration_hours"] * duration_multiplier
                ),
                "assigned_to": action["assigned_to"],
            }
            scaled_actions.append(scaled_action)

        return scaled_actions

    def _get_scaled_resources(
        self, event_type: str, severity: int
    ) -> List[Dict[str, Any]]:
        """Get resources scaled based on severity."""
        base_resources = self.resource_templates.get(event_type, [])

        scaled_resources = []
        severity_multiplier = 0.5 + (severity / 100)

        for resource in base_resources:
            scaled_resource = {
                "resource_type": resource["resource_type"],
                "quantity": int(resource["quantity"] * severity_multiplier),
                "priority": resource["priority"],
            }
            scaled_resources.append(scaled_resource)

        return scaled_resources

    def _estimate_affected_population(
        self, event_type: str, severity: int, raw_data: Dict[str, Any]
    ) -> int:
        """Estimate affected population (simplified heuristic)."""
        base_affected = {
            "extreme_rainfall": 50000,
            "flood_risk": 100000,
            "extreme_heat": 200000,
            "water_shortage": 150000,
            "severe_weather": 80000,
            "earthquake": 250000,
        }

        base = base_affected.get(event_type, 50000)
        # Scale by severity
        estimated = base * (severity / 50)
        return int(estimated)

    def _estimate_damage_cost(
        self, event_type: str, severity: int, raw_data: Dict[str, Any]
    ) -> float:
        """Estimate potential damage in USD (simplified heuristic)."""
        base_cost = {
            "extreme_rainfall": 500000,
            "flood_risk": 5000000,
            "extreme_heat": 1000000,
            "water_shortage": 2000000,
            "severe_weather": 3000000,
            "earthquake": 50000000,
        }

        base = base_cost.get(event_type, 1000000)
        # Scale by severity
        estimated = base * (severity / 50) * (1 + (severity / 100))
        return estimated


ai_planner = AIPlanningEngine()
