"""
Configuration management using Pydantic Settings.

This module provides centralized configuration for the backend application,
loading settings from environment variables with validation and type safety.
"""

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Temporal Configuration
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"

    # Security Configuration
    jwt_secret: str  # Required - no default
    jwt_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"

    # API Configuration
    api_cors_origins: List[str] = ["http://localhost:3000"]
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api"

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"

    # Development Configuration
    debug: bool = False
    enable_docs: bool = True

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate that JWT_SECRET is set and secure."""
        if not v or len(v) < 32:
            raise ValueError(
                "JWT_SECRET must be set and at least 32 characters long. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format is valid."""
        valid_formats = {"json", "text"}
        v_lower = v.lower()
        if v_lower not in valid_formats:
            raise ValueError(f"LOG_FORMAT must be one of {valid_formats}")
        return v_lower


# Singleton settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Export for convenience
settings = get_settings()
