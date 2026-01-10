"""
Configuration management for authorization service.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ServiceConfig(BaseModel):
    """Service configuration."""
    name: str = "authz-service"
    version: str = "1.0.0"
    port: int = 8002
    host: str = "0.0.0.0"
    environment: str = "development"


class JWTConfig(BaseModel):
    """JWT configuration."""
    secret: str = Field(..., description="JWT secret key")
    algorithm: str = "HS256"


class APIConfig(BaseModel):
    """API configuration."""
    key: str = Field(..., description="Service API key")


class EntityServiceConfig(BaseModel):
    """Entity service configuration."""
    base_url: str = "http://localhost:8001"
    timeout: float = 5.0
    retry_attempts: int = 3


class CacheConfig(BaseModel):
    """Cache configuration."""
    policy_ttl: int = 300  # 5 minutes
    role_ttl: int = 120  # 2 minutes
    decision_ttl: int = 30  # 30 seconds
    max_size: int = 10000


class RateLimitConfig(BaseModel):
    """Rate limit configuration."""
    per_user: int = 1000
    per_tenant: int = 10000
    per_ip: int = 5000
    window: int = 60  # seconds


class CORSConfig(BaseModel):
    """CORS configuration."""
    allow_origins: list = ["*"]
    allow_credentials: bool = True
    allow_methods: list = ["*"]
    allow_headers: list = ["*"]


class AppConfig(BaseSettings):
    """Application configuration."""
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    jwt: JWTConfig
    api: APIConfig
    entity_service: EntityServiceConfig = Field(default_factory=EntityServiceConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @classmethod
    def load_from_yaml(cls, config_path: str = "config/app.yaml") -> "AppConfig":
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Override with environment variables
        jwt_secret = os.getenv("JWT_SECRET", config_data.get("jwt", {}).get("secret"))
        api_key = os.getenv("API_KEY", config_data.get("api", {}).get("key"))
        entity_service_url = os.getenv("ENTITY_SERVICE_URL", 
                                       config_data.get("entity_service", {}).get("base_url"))
        
        if jwt_secret:
            config_data.setdefault("jwt", {})["secret"] = jwt_secret
        if api_key:
            config_data.setdefault("api", {})["key"] = api_key
        if entity_service_url:
            config_data.setdefault("entity_service", {})["base_url"] = entity_service_url
        
        return cls(**config_data)


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.load_from_yaml()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration from file."""
    global _config
    _config = AppConfig.load_from_yaml()
    return _config
