"""
Integration tests for release flow using test factories.

Tests the complete flow from authentication to release queries.
"""

import pytest
from httpx import AsyncClient

from tests.factories import ReleaseFactory, UserFactory


pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_release_list_flow(client: AsyncClient):
    """Test listing releases after authentication."""
    # This would require a running API and Temporal server
    # For now, this is a template for future integration tests

    # 1. Login
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123",
        },
    )

    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data

    # 2. Get releases with token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    releases_response = await client.get("/api/releases", headers=headers)

    assert releases_response.status_code == 200
    data = releases_response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_token_refresh_flow(client: AsyncClient):
    """Test token refresh functionality."""
    # 1. Login
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": "admin@example.com",
            "password": "admin123",
        },
    )

    assert login_response.status_code == 200
    token_data = login_response.json()
    refresh_token = token_data["refresh_token"]

    # 2. Refresh token
    refresh_response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 200
    new_token_data = refresh_response.json()
    assert "access_token" in new_token_data
    assert "refresh_token" in new_token_data
    assert new_token_data["access_token"] != token_data["access_token"]


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test that endpoints require authentication."""
    # Try to access releases without token
    response = await client.get("/api/releases")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    """Test that invalid tokens are rejected."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = await client.get("/api/releases", headers=headers)

    assert response.status_code == 401
