"""
Unit tests for authentication service.

Tests user authentication, token creation, and user management.
"""

import pytest

from src.services.auth_service import AuthService, AuthenticationError, UserNotFoundError
from src.models.auth import Token, User


@pytest.fixture
def auth_service() -> AuthService:
    """Create auth service instance for testing."""
    return AuthService()


def test_authenticate_user_success(auth_service: AuthService) -> None:
    """Test successful user authentication."""
    user = auth_service.authenticate_user("admin@example.com", "admin123")

    assert user.email == "admin@example.com"
    assert user.is_active is True
    assert user.is_admin is True
    assert user.last_login is not None


def test_authenticate_user_invalid_email(auth_service: AuthService) -> None:
    """Test authentication fails with invalid email."""
    with pytest.raises(AuthenticationError):
        auth_service.authenticate_user("nonexistent@example.com", "admin123")


def test_authenticate_user_invalid_password(auth_service: AuthService) -> None:
    """Test authentication fails with invalid password."""
    with pytest.raises(AuthenticationError):
        auth_service.authenticate_user("admin@example.com", "wrongpassword")


def test_create_user_token(auth_service: AuthService) -> None:
    """Test JWT token creation for user."""
    user = auth_service.authenticate_user("admin@example.com", "admin123")
    token = auth_service.create_user_token(user)

    assert isinstance(token, Token)
    assert token.access_token is not None
    assert len(token.access_token) > 0
    assert token.token_type == "bearer"
    assert token.expires_in == 1800  # 30 minutes in seconds


def test_get_user_by_email(auth_service: AuthService) -> None:
    """Test getting user by email."""
    user = auth_service.get_user_by_email("admin@example.com")

    assert isinstance(user, User)
    assert user.email == "admin@example.com"
    assert user.full_name == "Admin User"
    assert user.is_admin is True
    assert user.is_active is True
    # Ensure password is not exposed
    assert not hasattr(user, "hashed_password")


def test_get_user_by_email_not_found(auth_service: AuthService) -> None:
    """Test getting non-existent user by email."""
    with pytest.raises(UserNotFoundError):
        auth_service.get_user_by_email("nonexistent@example.com")


def test_get_user_by_id(auth_service: AuthService) -> None:
    """Test getting user by ID."""
    # First get user to get ID
    user = auth_service.get_user_by_email("admin@example.com")

    # Then get by ID
    user_by_id = auth_service.get_user_by_id(user.id)

    assert user_by_id.id == user.id
    assert user_by_id.email == user.email


def test_get_user_by_id_not_found(auth_service: AuthService) -> None:
    """Test getting non-existent user by ID."""
    with pytest.raises(UserNotFoundError):
        auth_service.get_user_by_id("nonexistent-id")


def test_create_new_user(auth_service: AuthService) -> None:
    """Test creating a new user."""
    new_user = auth_service.create_user(
        email="newuser@example.com",
        password="newpassword123",
        full_name="New User",
        is_admin=False,
    )

    assert new_user.email == "newuser@example.com"
    assert new_user.full_name == "New User"
    assert new_user.is_admin is False
    assert new_user.is_active is True

    # Verify user can authenticate
    authenticated_user = auth_service.authenticate_user("newuser@example.com", "newpassword123")
    assert authenticated_user.email == "newuser@example.com"


def test_create_duplicate_user(auth_service: AuthService) -> None:
    """Test creating duplicate user fails."""
    with pytest.raises(ValueError):
        auth_service.create_user(
            email="admin@example.com",  # Already exists
            password="password",
        )


def test_default_users_exist(auth_service: AuthService) -> None:
    """Test default admin and regular users exist."""
    # Admin user
    admin = auth_service.get_user_by_email("admin@example.com")
    assert admin.is_admin is True
    assert admin.is_active is True

    # Regular user
    user = auth_service.get_user_by_email("user@example.com")
    assert user.is_admin is False
    assert user.is_active is True


def test_regular_user_authentication(auth_service: AuthService) -> None:
    """Test regular (non-admin) user can authenticate."""
    user = auth_service.authenticate_user("user@example.com", "user123")

    assert user.email == "user@example.com"
    assert user.is_admin is False
    assert user.is_active is True
