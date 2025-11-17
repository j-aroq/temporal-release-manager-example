"""
Authentication API endpoints.

Provides login and user information endpoints with JWT authentication.
"""

from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..models.auth import Token, User, TokenData
from ..services.auth_service import get_auth_service, AuthService, AuthenticationError, UserNotFoundError
from ..core.security import verify_access_token

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# OAuth2 password bearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        token: JWT access token from Authorization header
        auth_service: Authentication service instance

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify and decode token
    payload = verify_access_token(token)
    if payload is None:
        logger.warning("Invalid or expired token")
        raise credentials_exception

    # Extract user email from token
    email: str | None = payload.get("sub")
    if email is None:
        logger.warning("Token missing 'sub' claim")
        raise credentials_exception

    # Get user from service
    try:
        user = auth_service.get_user_by_email(email)
    except UserNotFoundError:
        logger.warning(f"User not found for token: {email}")
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    User login endpoint.

    Authenticates user with email/password and returns JWT access token.

    Args:
        form_data: OAuth2 password form with username (email) and password
        auth_service: Authentication service instance

    Returns:
        Token response with access_token, type, and expiration

    Raises:
        HTTPException: If authentication fails (401)
    """
    try:
        # Authenticate user (username field contains email)
        user = auth_service.authenticate_user(form_data.username, form_data.password)

        # Create access token
        token = auth_service.create_user_token(user)

        logger.info(f"User logged in: {user.email}")
        return token

    except AuthenticationError as e:
        logger.warning(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/auth/me", response_model=User)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current authenticated user information.

    Args:
        current_user: Current user from JWT token (injected by dependency)

    Returns:
        Current user information
    """
    return current_user
