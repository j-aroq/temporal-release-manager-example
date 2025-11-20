"""
User-friendly error messages for common errors.

Maps technical exceptions to user-friendly messages suitable for display in UI.
"""

from typing import Dict


# Error message mapping for user-friendly display
ERROR_MESSAGES: Dict[str, str] = {
    "WorkflowNotFoundError": (
        "This release is no longer available. It may have completed, been removed, "
        "or the workflow ID is incorrect."
    ),
    "TemporalConnectionError": (
        "Unable to connect to the workflow service. The service may be temporarily "
        "unavailable. Please try again in a moment."
    ),
    "QueryTimeoutError": (
        "The request took too long to complete. The workflow may be processing a "
        "large amount of data. Please try again."
    ),
    "EntityNotFoundError": (
        "The requested release or entity could not be found. It may have been removed "
        "or completed."
    ),
    "AuthenticationError": (
        "Authentication failed. Please check your credentials and try again."
    ),
    "UserNotFoundError": (
        "User account not found. Please check your email address."
    ),
    "TemporalClientError": (
        "An error occurred while communicating with the workflow service. "
        "Please try again or contact support if the problem persists."
    ),
    "RateLimitExceeded": (
        "Too many requests. Please wait a moment before trying again."
    ),
    "ValidationError": (
        "The provided data is invalid. Please check your input and try again."
    ),
}


# HTTP status code to user message mapping
HTTP_ERROR_MESSAGES: Dict[int, str] = {
    400: "The request was invalid. Please check your input.",
    401: "You need to log in to access this resource.",
    403: "You don't have permission to access this resource.",
    404: "The requested resource was not found.",
    429: "Too many requests. Please slow down and try again later.",
    500: "An internal server error occurred. We're working to fix it.",
    503: "The service is temporarily unavailable. Please try again later.",
}


def get_user_friendly_error(exception_type: str, default: str = None) -> str:
    """
    Get user-friendly error message for an exception type.

    Args:
        exception_type: Name of the exception class
        default: Default message if no mapping found

    Returns:
        User-friendly error message
    """
    return ERROR_MESSAGES.get(
        exception_type,
        default or "An unexpected error occurred. Please try again.",
    )


def get_http_error_message(status_code: int) -> str:
    """
    Get user-friendly message for HTTP status code.

    Args:
        status_code: HTTP status code

    Returns:
        User-friendly error message
    """
    return HTTP_ERROR_MESSAGES.get(
        status_code,
        "An error occurred while processing your request.",
    )
