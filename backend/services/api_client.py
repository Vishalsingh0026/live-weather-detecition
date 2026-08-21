import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class APIClientService:
    """Service for making HTTP requests to external APIs."""

    def __init__(self, timeout: int = 30):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        logger.info("API Client initialized")

    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            logger.info("API Client closed")

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GET request to API."""
        if not self.session:
            raise RuntimeError("API Client not initialized. Call initialize() first.")

        try:
            async with self.session.get(
                url, headers=headers, params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched from {url}")
                    return {"success": True, "data": data, "status": response.status}
                else:
                    logger.warning(f"API request failed: {url} - Status {response.status}")
                    return {
                        "success": False,
                        "error": f"Status {response.status}",
                        "status": response.status,
                    }
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching {url}: {e}")
            return {"success": False, "error": str(e), "status": None}
        except Exception as e:
            logger.error(f"Unexpected error in API call to {url}: {e}")
            return {"success": False, "error": str(e), "status": None}

    async def fetch_weather_data(
        self, latitude: float, longitude: float, api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch weather data from Open-Meteo API (free, no key required)."""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,precipitation,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "temperature_unit": "celsius",
            "timezone": "IST",
        }
        return await self.get(url, params=params)

    async def fetch_earthquake_data(self) -> Dict[str, Any]:
        """Fetch earthquake data from USGS API (real-time)."""
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
        return await self.get(url)

    async def fetch_air_quality_data(
        self, latitude: float, longitude: float
    ) -> Dict[str, Any]:
        """Fetch air quality data from Open-Meteo Air Quality API."""
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "pm10,pm2_5,o3,no2,so2,co",
            "timezone": "IST",
        }
        return await self.get(url, params=params)

    async def fetch_rainfall_data(self) -> Dict[str, Any]:
        """Fetch rainfall data from public sources."""
        # Using Open-Meteo historical/forecast data
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 20.5937,  # India center
            "longitude": 78.9629,
            "hourly": "precipitation",
            "timezone": "IST",
        }
        return await self.get(url, params=params)

    async def fetch_flood_forecast(self) -> Dict[str, Any]:
        """Fetch flood risk forecast from available public APIs."""
        # This would integrate with actual flood forecasting APIs
        # For now, using rainfall as proxy indicator
        return await self.fetch_rainfall_data()


api_client = APIClientService()
