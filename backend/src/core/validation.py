"""
Input validation utilities for API endpoints.

Provides sanitization and validation functions to prevent injection attacks
and ensure data integrity.
"""

import re
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


def validate_entity_id_format(entity_id: str, entity_type: str) -> None:
    """
    Validate entity ID format and prevent injection attacks.

    Args:
        entity_id: Entity ID to validate
        entity_type: Expected entity type prefix (e.g., "wave", "cluster")

    Raises:
        HTTPException: If ID format is invalid or contains suspicious characters

    Examples:
        >>> validate_entity_id_format("release:abc-123", "release")  # Valid
        >>> validate_entity_id_format("release:abc'; DROP TABLE", "release")  # Raises
    """
    # Check for required prefix
    if not entity_id.startswith(f"{entity_type}:"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{entity_type.capitalize()} ID must start with '{entity_type}:'",
        )

    # Extract the actual ID part after the prefix
    id_value = entity_id[len(entity_type) + 1 :]

    # Validate ID contains only safe characters (alphanumeric, dash, underscore)
    # This prevents SQL injection, command injection, and other attacks
    if not re.match(r"^[a-zA-Z0-9_-]+$", id_value):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {entity_type} ID format. Only alphanumeric characters, dashes, and underscores are allowed.",
        )

    # Check length constraints (prevent DOS via extremely long IDs)
    if len(entity_id) > 200:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{entity_type.capitalize()} ID is too long (max 200 characters).",
        )

    if len(id_value) < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{entity_type.capitalize()} ID cannot be empty.",
        )


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing potentially dangerous characters.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        HTTPException: If string exceeds max length
    """
    if len(value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Input too long (max {max_length} characters).",
        )

    # Remove null bytes and other control characters
    sanitized = value.replace("\x00", "")

    # Remove other potentially dangerous control characters
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)

    return sanitized.strip()


def validate_pagination_params(page: int, page_size: int) -> None:
    """
    Validate pagination parameters to prevent abuse.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page number must be at least 1.",
        )

    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page size must be at least 1.",
        )

    if page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page size cannot exceed 100 items.",
        )

    # Prevent DOS by limiting total offset
    max_offset = 10000
    if (page - 1) * page_size > max_offset:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot access results beyond offset {max_offset}.",
        )


def validate_email(email: str) -> None:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Raises:
        HTTPException: If email format is invalid
    """
    # Basic email validation
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email format.",
        )

    if len(email) > 254:  # RFC 5321
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email address is too long.",
        )


def validate_password_strength(password: str) -> None:
    """
    Validate password meets minimum security requirements.

    Args:
        password: Password to validate

    Raises:
        HTTPException: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long.",
        )

    if len(password) > 72:  # bcrypt limit
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must not exceed 72 characters.",
        )

    # Check for at least one letter and one number
    if not re.search(r"[a-zA-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one letter.",
        )

    if not re.search(r"[0-9]", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must contain at least one number.",
        )


def sanitize_log_output(data: Any) -> Any:
    """
    Sanitize data before logging to prevent log injection attacks.

    Args:
        data: Data to sanitize (can be string, dict, list, etc.)

    Returns:
        Sanitized data safe for logging
    """
    if isinstance(data, str):
        # Remove newlines and carriage returns to prevent log injection
        sanitized = data.replace("\n", "\\n").replace("\r", "\\r")
        # Truncate very long strings
        if len(sanitized) > 500:
            sanitized = sanitized[:497] + "..."
        return sanitized

    elif isinstance(data, dict):
        return {k: sanitize_log_output(v) for k, v in data.items()}

    elif isinstance(data, list):
        return [sanitize_log_output(item) for item in data]

    return data
