"""
Unit tests for test data factories.

Ensures factories create valid model instances.
"""

import pytest
from tests.factories import (
    ReleaseFactory,
    WaveFactory,
    ClusterFactory,
    BundleFactory,
    AppFactory,
    UserFactory,
    TokenFactory,
)


def test_release_factory_creates_valid_release():
    """Test ReleaseFactory creates valid Release."""
    release = ReleaseFactory.create()

    assert release.id.startswith("release:")
    assert release.workflow_id.startswith("wf_")
    assert release.state == "in_progress"
    assert len(release.wave_ids) == 2
    assert all(wid.startswith("wave:") for wid in release.wave_ids)


def test_release_factory_batch_creation():
    """Test creating multiple releases."""
    releases = ReleaseFactory.create_batch(5, state="completed")

    assert len(releases) == 5
    assert all(r.state == "completed" for r in releases)
    # All should have unique IDs
    ids = [r.id for r in releases]
    assert len(ids) == len(set(ids))


def test_wave_factory_creates_valid_wave():
    """Test WaveFactory creates valid Wave."""
    wave = WaveFactory.create()

    assert wave.id.startswith("wave:")
    assert wave.release_id == "release:test-rel"
    assert wave.sequence == 1
    assert len(wave.cluster_ids) == 2


def test_cluster_factory_creates_valid_cluster():
    """Test ClusterFactory creates valid Cluster."""
    cluster = ClusterFactory.create()

    assert cluster.id.startswith("cluster:")
    assert cluster.wave_id == "wave:wave-1"
    assert cluster.state == "deploying"
    assert cluster.bundle_id == "bundle:bundle-1"


def test_bundle_factory_creates_valid_bundle():
    """Test BundleFactory creates valid Bundle."""
    bundle = BundleFactory.create()

    assert bundle.id.startswith("bundle:")
    assert bundle.cluster_id == "cluster:test-cluster"
    assert len(bundle.app_ids) == 3


def test_app_factory_creates_valid_app():
    """Test AppFactory creates valid App."""
    app = AppFactory.create()

    assert app.id.startswith("app:")
    assert app.bundle_id == "bundle:test-bundle"
    assert app.version == "v1.0.0"


def test_user_factory_creates_valid_user():
    """Test UserFactory creates valid User."""
    user = UserFactory.create()

    assert "@example.com" in user.email
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_admin is False


def test_user_factory_with_password():
    """Test UserFactory creates UserInDB with hashed password."""
    user = UserFactory.create_with_password(password="testpass123")

    assert hasattr(user, "hashed_password")
    assert user.hashed_password != "testpass123"  # Should be hashed


def test_token_factory_creates_valid_token():
    """Test TokenFactory creates valid Token."""
    token = TokenFactory.create()

    assert token.token_type == "bearer"
    assert token.expires_in == 1800
    assert token.access_token is not None
    assert token.refresh_token is not None
