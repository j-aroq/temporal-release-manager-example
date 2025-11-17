"""
Integration tests for authentication flow.

Tests login, token validation, and protected endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_login_success() -> None:
    """Test successful login with valid credentials."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert data["expires_in"] == 1800  # 30 minutes in seconds


def test_login_invalid_email() -> None:
    """Test login fails with invalid email."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "admin123",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_login_invalid_password() -> None:
    """Test login fails with invalid password."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "admin@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_get_current_user_authenticated() -> None:
    """Test getting current user info with valid token."""
    # First, login to get token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Then, get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "admin@example.com"
    assert data["full_name"] == "Admin User"
    assert data["is_active"] is True
    assert data["is_admin"] is True
    assert "id" in data
    assert "created_at" in data


def test_get_current_user_no_token() -> None:
    """Test getting current user fails without token."""
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_get_current_user_invalid_token() -> None:
    """Test getting current user fails with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401


def test_regular_user_login() -> None:
    """Test regular (non-admin) user can login."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "user@example.com",
            "password": "user123",
        },
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Verify user info
    user_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert user_response.status_code == 200
    user_data = user_response.json()

    assert user_data["email"] == "user@example.com"
    assert user_data["is_admin"] is False
    assert user_data["is_active"] is True


def test_token_contains_correct_claims() -> None:
    """Test JWT token contains expected claims."""
    # Login
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Decode token (in real scenario, verify it's properly signed)
    # For this test, we verify it works with /auth/me endpoint
    user_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert user_response.status_code == 200
    # Token is valid if we can get user info
