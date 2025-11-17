"""
Unit tests for configuration management.

Tests Settings validation and environment variable loading.
"""

import pytest
from pydantic import ValidationError

from src.core.config import Settings


def test_settings_with_valid_jwt_secret() -> None:
    """Test Settings with valid JWT secret."""
    settings = Settings(
        jwt_secret="this-is-a-test-secret-that-is-long-enough-32-chars",
        temporal_host="localhost:7233",
    )
    assert settings.jwt_secret == "this-is-a-test-secret-that-is-long-enough-32-chars"
    assert settings.temporal_host == "localhost:7233"
    assert settings.temporal_namespace == "default"


def test_settings_jwt_secret_too_short() -> None:
    """Test Settings rejects short JWT secret."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(jwt_secret="short")

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("JWT_SECRET" in str(error) for error in errors)


def test_settings_invalid_log_level() -> None:
    """Test Settings rejects invalid log level."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            jwt_secret="this-is-a-test-secret-that-is-long-enough-32-chars",
            log_level="INVALID",
        )

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("LOG_LEVEL" in str(error) for error in errors)


def test_settings_invalid_log_format() -> None:
    """Test Settings rejects invalid log format."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            jwt_secret="this-is-a-test-secret-that-is-long-enough-32-chars",
            log_format="xml",
        )

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("LOG_FORMAT" in str(error) for error in errors)


def test_settings_defaults() -> None:
    """Test Settings applies correct defaults."""
    settings = Settings(
        jwt_secret="this-is-a-test-secret-that-is-long-enough-32-chars",
    )

    assert settings.temporal_host == "localhost:7233"
    assert settings.temporal_namespace == "default"
    assert settings.jwt_expire_minutes == 30
    assert settings.jwt_algorithm == "HS256"
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.api_prefix == "/api"
    assert settings.log_level == "INFO"
    assert settings.log_format == "json"
    assert settings.debug is False
    assert settings.enable_docs is True
