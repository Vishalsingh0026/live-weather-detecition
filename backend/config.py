import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    app_name: str = "BharatResilience AI"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = True

    # Database
    database_url: str = "postgresql://bharatresilience:Vishal12%40@localhost:1234/bharat_resilience"
    sqlalchemy_echo: bool = True

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_password: str = ""
    cache_ttl: int = 300

    # JWT
    secret_key: str = "your-super-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # External APIs
    weather_api_key: str = ""
    weather_api_provider: str = "open-meteo"
    earthquake_api_url: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    flood_api_url: str = "https://api.flooddata.com/v1"
    water_api_url: str = ""

    # Alerts
    alert_threshold: int = 70
    email_from: str = "alerts@bharatresilience.ai"
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""

    # Geospatial
    default_latitude: float = 20.5937
    default_longitude: float = 78.9629
    default_country: str = "India"

    # API Rate Limiting
    api_rate_limit: int = 100
    api_rate_limit_window: int = 60

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Monitoring
    sentry_dsn: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
