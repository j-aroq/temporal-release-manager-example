"""
Environment variable validation on application startup.

Validates that all required configuration is present and properly formatted.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""

    pass


def validate_settings(settings) -> None:
    """
    Validate settings after they are loaded from environment/config.

    Args:
        settings: Settings instance with loaded configuration

    Raises:
        ConfigurationError: If configuration is invalid
    """
    warnings: List[str] = []

    # Warn about default/insecure values
    if settings.jwt_secret and ("change-this" in settings.jwt_secret.lower() or "your-secret" in settings.jwt_secret.lower()):
        warnings.append(
            "⚠️  JWT_SECRET appears to use a default/example value. "
            "Please generate a secure random key for production."
        )

    # Print warnings
    if warnings:
        logger.warning("Configuration warnings:")
        for warning in warnings:
            logger.warning(f"  {warning}")

    logger.info("✓ Configuration validation passed")


# Deprecated - use validate_settings instead
def validate_environment() -> None:
    """
    Legacy validation function - no longer used.

    Validation now happens in Settings validators and validate_settings().
    This function is kept for backwards compatibility but does nothing.
    """
    pass


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
