"""
Pydantic models for authentication and user management.

Defines User and Token models for JWT authentication.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User model for authentication."""

    id: str = Field(..., description="Unique user identifier (UUID)")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(True, description="Whether user account is active")
    is_admin: bool = Field(False, description="Whether user has admin privileges")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last successful login timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "Jane Doe",
                "is_active": True,
                "is_admin": False,
                "created_at": "2025-11-01T09:00:00Z",
                "last_login": "2025-11-06T08:30:00Z",
            }
        }
    }


class UserInDB(User):
    """User model with hashed password (internal use only)."""

    hashed_password: str = Field(..., description="Bcrypt-hashed password")


class Token(BaseModel):
    """JWT token response model."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    }


class TokenData(BaseModel):
    """Data extracted from JWT token."""

    email: Optional[str] = None
    user_id: Optional[str] = None
