import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from utils import config, init_utils


# Ensure utils-config reads from the service config directory (respects CONFIG_DIR override)
CONFIG_DIR = Path(os.environ.get("CONFIG_DIR", "config"))
init_utils(str(CONFIG_DIR))

def _get_bool(key: str, default: bool) -> bool:
    value = config.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    return bool(value)


def _get_int(key: str, default: int) -> int:
    try:
        return int(config.get(key, default))
    except (TypeError, ValueError):
        return default


def _get_float(key: str, default: float) -> float:
    try:
        return float(config.get(key, default))
    except (TypeError, ValueError):
        return default


class Settings(BaseSettings):
    """Authorization service settings loaded via utils.config defaults with env overrides."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Service Configuration
    SERVICE_NAME: str = config.get("service.name", "authz-service")
    SERVICE_VERSION: str = config.get("service.version", "1.0.0")
    ENVIRONMENT: str = config.get("service.environment", "development")
    HOST: str = config.get("server.host", "0.0.0.0")
    PORT: int = _get_int("server.port", 8001)
    WORKERS: int = _get_int("service.workers", 4)
    DEBUG: bool = _get_bool("service.debug", True)

    # Security Configuration
    JWT_SECRET_KEY: str = config.get("jwt.access_secret", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = config.get("jwt.algorithm", "HS256")
    API_KEY: str = config.get("api.key", "test-api-key")  # Default for testing
    API_KEY_HEADER: str = config.get("api_key.header", "X-API-Key")
    
    # Testing
    TESTING: bool = os.getenv("TESTING", "false").lower() in ("true", "1", "yes")

    # Entity Service Configuration
    ENTITY_SERVICE_URL: str = config.get("external_services.entity_service.url", "http://localhost:8002")
    ENTITY_SERVICE_TIMEOUT: int = _get_int("external_services.entity_service.timeout", 10)
    ENTITY_SERVICE_RETRY_ATTEMPTS: int = _get_int("external_services.entity_service.retry_attempts", 3)

    # Cache Configuration
    CACHE_TTL_SECONDS: int = _get_int("cache.ttl_seconds", 3600)
    CACHE_ENABLED: bool = _get_bool("cache.enabled", True)

    # Logging Configuration
    LOG_LEVEL: str = config.get("logging.level", "INFO")
    LOG_FORMAT: str = config.get("logging.format", "json")

    # Database Configuration (optional)
    DATABASE_URL: Optional[str] = config.get("database.url")


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
