"""
Environment variable validation on application startup.

Validates that all required configuration is present and properly formatted.
"""

import os
import sys
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

    pass


def validate_environment() -> None:
    """
    Validate all required environment variables on startup.

    Raises:
        ConfigurationError: If required variables are missing or invalid
    """
    errors: List[str] = []

    # Check required variables
    required_vars = {
        "JWT_SECRET": "JWT secret key for token signing",
        "TEMPORAL_HOST": "Temporal server address",
    }

    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"Missing required variable: {var} ({description})")

    # Validate JWT_SECRET length
    jwt_secret = os.getenv("JWT_SECRET", "")
    if jwt_secret and len(jwt_secret) < 32:
        errors.append(
            f"JWT_SECRET must be at least 32 characters (current: {len(jwt_secret)}). "
            "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    # Warn about default/insecure values
    warnings: List[str] = []

    if jwt_secret and ("change-this" in jwt_secret.lower() or "your-secret" in jwt_secret.lower()):
        warnings.append(
            "⚠️  JWT_SECRET appears to use a default/example value. "
            "Please generate a secure random key for production."
        )

    # Validate CORS origins format
    cors_origins = os.getenv("API_CORS_ORIGINS")
    if cors_origins and not (cors_origins.startswith("[") and cors_origins.endswith("]")):
        warnings.append(
            "API_CORS_ORIGINS should be a JSON array (e.g., '[\"http://localhost:3000\"]')"
        )

    # Validate log level
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level not in valid_levels:
        warnings.append(f"LOG_LEVEL '{log_level}' is invalid. Valid: {valid_levels}")

    # Print warnings
    if warnings:
        logger.warning("Configuration warnings:")
        for warning in warnings:
            logger.warning(f"  {warning}")

    # Raise errors if any
    if errors:
        error_msg = "Configuration validation failed:\n"
        for error in errors:
            error_msg += f"  ❌ {error}\n"
        raise ConfigurationError(error_msg)

    logger.info("✓ Environment validation passed")


def check_optional_services() -> None:
    """
    Check connectivity to optional services and log warnings if unavailable.

    This is called after startup to not block application start.
    """
    # Could add checks for:
    # - Temporal server connectivity
    # - Database connectivity (if added)
    # - Redis connectivity (if caching added)
    pass
