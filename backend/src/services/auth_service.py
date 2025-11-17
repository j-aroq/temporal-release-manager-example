"""
Authentication service for user management and JWT token operations.

Provides user authentication, password verification, and token creation.
For development, uses an in-memory user store with a default admin user.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid
import logging

from ..models.auth import User, UserInDB, Token, TokenData
from ..core.security import hash_password, verify_password, create_access_token
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class UserNotFoundError(Exception):
    """Raised when user is not found."""

    pass


class AuthService:
    """
    Authentication service for user management and JWT operations.

    For development, maintains an in-memory user store.
    In production, this should be replaced with a database backend.
    """

    def __init__(self) -> None:
        """Initialize authentication service with default users."""
        self.settings = get_settings()
        self._users: Dict[str, UserInDB] = {}
        self._create_default_users()

    def _create_default_users(self) -> None:
        """Create default users for development."""
        # Default admin user
        admin_user = UserInDB(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            full_name="Admin User",
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow(),
        )
        self._users[admin_user.email] = admin_user

        # Default regular user
        regular_user = UserInDB(
            id=str(uuid.uuid4()),
            email="user@example.com",
            hashed_password=hash_password("user123"),
            full_name="Regular User",
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
        )
        self._users[regular_user.email] = regular_user

        logger.info("Created default users for development")
        logger.info(f"Admin user: {admin_user.email} / admin123")
        logger.info(f"Regular user: {regular_user.email} / user123")

    def authenticate_user(self, email: str, password: str) -> UserInDB:
        """
        Authenticate user with email and password.

        Args:
            email: User email address
            password: Plaintext password

        Returns:
            Authenticated user with hashed password

        Raises:
            AuthenticationError: If authentication fails
        """
        user = self._users.get(email)

        if not user:
            logger.warning(f"Authentication failed: user not found - {email}")
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {email}")
            raise AuthenticationError("User account is inactive")

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password - {email}")
            raise AuthenticationError("Invalid email or password")

        # Update last login
        user.last_login = datetime.utcnow()
        logger.info(f"User authenticated successfully: {email}")

        return user

    def create_user_token(self, user: UserInDB) -> Token:
        """
        Create JWT access token for authenticated user.

        Args:
            user: Authenticated user

        Returns:
            Token response with access_token, type, and expiration
        """
        # Create token data
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "is_admin": user.is_admin,
        }

        # Create access token
        expires_delta = timedelta(minutes=self.settings.jwt_expire_minutes)
        access_token = create_access_token(token_data, expires_delta)

        logger.info(f"Created access token for user: {user.email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.settings.jwt_expire_minutes * 60,  # Convert to seconds
        )

    def get_user_by_email(self, email: str) -> User:
        """
        Get user by email address (without password hash).

        Args:
            email: User email address

        Returns:
            User model without password

        Raises:
            UserNotFoundError: If user not found
        """
        user_in_db = self._users.get(email)

        if not user_in_db:
            raise UserNotFoundError(f"User not found: {email}")

        # Return User without hashed_password
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            is_active=user_in_db.is_active,
            is_admin=user_in_db.is_admin,
            created_at=user_in_db.created_at,
            last_login=user_in_db.last_login,
        )

    def get_user_by_id(self, user_id: str) -> User:
        """
        Get user by ID (without password hash).

        Args:
            user_id: User ID

        Returns:
            User model without password

        Raises:
            UserNotFoundError: If user not found
        """
        for user in self._users.values():
            if user.id == user_id:
                return User(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    is_admin=user.is_admin,
                    created_at=user.created_at,
                    last_login=user.last_login,
                )

        raise UserNotFoundError(f"User not found with ID: {user_id}")

    def create_user(
        self, email: str, password: str, full_name: Optional[str] = None, is_admin: bool = False
    ) -> User:
        """
        Create a new user.

        Args:
            email: User email address
            password: Plaintext password
            full_name: Optional full name
            is_admin: Whether user has admin privileges

        Returns:
            Created user (without password hash)

        Raises:
            ValueError: If user already exists
        """
        if email in self._users:
            raise ValueError(f"User already exists: {email}")

        user = UserInDB(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_active=True,
            is_admin=is_admin,
            created_at=datetime.utcnow(),
        )

        self._users[email] = user
        logger.info(f"Created new user: {email}")

        return User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login,
        )


# Global auth service instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or create global auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
