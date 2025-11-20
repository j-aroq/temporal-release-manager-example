"""
Test data factories for creating model instances.

Provides factory functions to easily create test data for entities, users, and releases.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from src.models.entities import Release, Wave, Cluster, Bundle, App
from src.models.auth import User, UserInDB, Token
from src.core.security import hash_password


class ReleaseFactory:
    """Factory for creating Release instances."""

    @staticmethod
    def create(
        release_id: Optional[str] = None,
        state: str = "in_progress",
        wave_count: int = 2,
        workflow_id: Optional[str] = None,
    ) -> Release:
        """
        Create a Release instance with optional customization.

        Args:
            release_id: Custom release ID (auto-generated if None)
            state: Release state (default: in_progress)
            wave_count: Number of wave IDs to include
            workflow_id: Custom workflow ID (auto-generated if None)

        Returns:
            Release instance
        """
        rel_id = release_id or f"release:test-{uuid4().hex[:8]}"
        wf_id = workflow_id or f"wf_{uuid4().hex[:12]}"

        return Release(
            id=rel_id,
            state=state,
            workflow_id=wf_id,
            wave_ids=[f"wave:wave-{i}" for i in range(1, wave_count + 1)],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @staticmethod
    def create_batch(count: int, **kwargs) -> List[Release]:
        """
        Create multiple Release instances.

        Args:
            count: Number of releases to create
            **kwargs: Additional arguments passed to create()

        Returns:
            List of Release instances
        """
        return [ReleaseFactory.create(**kwargs) for _ in range(count)]


class WaveFactory:
    """Factory for creating Wave instances."""

    @staticmethod
    def create(
        wave_id: Optional[str] = None,
        release_id: str = "release:test-rel",
        state: str = "in_progress",
        sequence: int = 1,
        cluster_count: int = 2,
    ) -> Wave:
        """
        Create a Wave instance.

        Args:
            wave_id: Custom wave ID (auto-generated if None)
            release_id: Parent release ID
            state: Wave state
            sequence: Wave sequence number
            cluster_count: Number of cluster IDs to include

        Returns:
            Wave instance
        """
        w_id = wave_id or f"wave:wave-{sequence}"

        return Wave(
            id=w_id,
            release_id=release_id,
            state=state,
            sequence=sequence,
            cluster_ids=[f"cluster:cluster-{i}" for i in range(1, cluster_count + 1)],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class ClusterFactory:
    """Factory for creating Cluster instances."""

    @staticmethod
    def create(
        cluster_id: Optional[str] = None,
        wave_id: str = "wave:wave-1",
        state: str = "deploying",
        name: Optional[str] = None,
    ) -> Cluster:
        """
        Create a Cluster instance.

        Args:
            cluster_id: Custom cluster ID (auto-generated if None)
            wave_id: Parent wave ID
            state: Cluster state
            name: Human-readable name

        Returns:
            Cluster instance
        """
        c_id = cluster_id or f"cluster:test-{uuid4().hex[:8]}"

        return Cluster(
            id=c_id,
            wave_id=wave_id,
            state=state,
            name=name or f"Test Cluster {c_id}",
            bundle_id=f"bundle:bundle-1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class BundleFactory:
    """Factory for creating Bundle instances."""

    @staticmethod
    def create(
        bundle_id: Optional[str] = None,
        cluster_id: str = "cluster:test-cluster",
        state: str = "deploying",
        app_count: int = 3,
    ) -> Bundle:
        """
        Create a Bundle instance.

        Args:
            bundle_id: Custom bundle ID (auto-generated if None)
            cluster_id: Parent cluster ID
            state: Bundle state
            app_count: Number of app IDs to include

        Returns:
            Bundle instance
        """
        b_id = bundle_id or f"bundle:test-{uuid4().hex[:8]}"

        return Bundle(
            id=b_id,
            cluster_id=cluster_id,
            state=state,
            name=f"Test Bundle {b_id}",
            app_ids=[f"app:app-{i}" for i in range(1, app_count + 1)],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class AppFactory:
    """Factory for creating App instances."""

    @staticmethod
    def create(
        app_id: Optional[str] = None,
        bundle_id: str = "bundle:test-bundle",
        state: str = "running",
        version: str = "v1.0.0",
    ) -> App:
        """
        Create an App instance.

        Args:
            app_id: Custom app ID (auto-generated if None)
            bundle_id: Parent bundle ID
            state: App state
            version: App version

        Returns:
            App instance
        """
        a_id = app_id or f"app:test-{uuid4().hex[:8]}"

        return App(
            id=a_id,
            bundle_id=bundle_id,
            state=state,
            name=f"Test App {a_id}",
            version=version,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )


class UserFactory:
    """Factory for creating User instances."""

    @staticmethod
    def create(
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_admin: bool = False,
    ) -> User:
        """
        Create a User instance.

        Args:
            email: User email (auto-generated if None)
            full_name: Full name
            is_active: Whether user is active
            is_admin: Whether user is admin

        Returns:
            User instance
        """
        user_id = str(uuid4())
        user_email = email or f"test{uuid4().hex[:8]}@example.com"

        return User(
            id=user_id,
            email=user_email,
            full_name=full_name or "Test User",
            is_active=is_active,
            is_admin=is_admin,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow() - timedelta(hours=1),
        )

    @staticmethod
    def create_with_password(
        email: Optional[str] = None,
        password: str = "testpass123",
        **kwargs,
    ) -> UserInDB:
        """
        Create a UserInDB instance with hashed password.

        Args:
            email: User email (auto-generated if None)
            password: Plaintext password to hash
            **kwargs: Additional arguments for User creation

        Returns:
            UserInDB instance with hashed password
        """
        user = UserFactory.create(email=email, **kwargs)

        return UserInDB(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login,
            hashed_password=hash_password(password),
        )


class TokenFactory:
    """Factory for creating Token instances."""

    @staticmethod
    def create(
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expires_in: int = 1800,
    ) -> Token:
        """
        Create a Token instance.

        Args:
            access_token: JWT access token (generated if None)
            refresh_token: JWT refresh token (generated if None)
            expires_in: Token expiration in seconds

        Returns:
            Token instance
        """
        return Token(
            access_token=access_token or f"test_token_{uuid4().hex}",
            refresh_token=refresh_token or f"test_refresh_{uuid4().hex}",
            token_type="bearer",
            expires_in=expires_in,
        )
