"""
Unit tests for entity models.

Tests Pydantic validation for Release, Wave, Cluster, Bundle, and App models.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from src.models.entities import Release, Wave, Cluster, Bundle, App, ReleaseHierarchy


def test_release_valid() -> None:
    """Test Release model with valid data."""
    release = Release(
        id="release:test-001",
        state="in_progress",
        workflow_id="wf_test_001",
        wave_ids=["wave:wave-1", "wave:wave-2"],
    )
    assert release.id == "release:test-001"
    assert release.state == "in_progress"
    assert release.workflow_id == "wf_test_001"
    assert len(release.wave_ids) == 2


def test_release_invalid_id_format() -> None:
    """Test Release rejects invalid ID format."""
    with pytest.raises(ValidationError):
        Release(
            id="invalid-id",  # Missing 'release:' prefix
            state="in_progress",
            workflow_id="wf_test",
        )


def test_release_invalid_wave_id() -> None:
    """Test Release rejects invalid Wave ID."""
    with pytest.raises(ValidationError):
        Release(
            id="release:test-001",
            state="in_progress",
            workflow_id="wf_test",
            wave_ids=["invalid:wave-1"],  # Wrong prefix
        )


def test_wave_valid() -> None:
    """Test Wave model with valid data."""
    wave = Wave(
        id="wave:wave-1",
        state="deploying",
        release_id="release:test-001",
        sequence=1,
        cluster_ids=["cluster:us-west", "cluster:us-east"],
    )
    assert wave.id == "wave:wave-1"
    assert wave.release_id == "release:test-001"
    assert wave.sequence == 1
    assert len(wave.cluster_ids) == 2


def test_wave_invalid_id_prefix() -> None:
    """Test Wave rejects invalid ID prefix."""
    with pytest.raises(ValidationError):
        Wave(
            id="release:wave-1",  # Wrong prefix
            state="deploying",
            release_id="release:test-001",
        )


def test_cluster_valid() -> None:
    """Test Cluster model with valid data."""
    cluster = Cluster(
        id="cluster:us-west",
        state="deploying",
        wave_id="wave:wave-1",
        name="US West Production",
        bundle_id="bundle:web-services",
    )
    assert cluster.id == "cluster:us-west"
    assert cluster.wave_id == "wave:wave-1"
    assert cluster.bundle_id == "bundle:web-services"
    assert cluster.name == "US West Production"


def test_cluster_exactly_one_bundle() -> None:
    """Test Cluster has exactly one bundle_id field."""
    cluster = Cluster(
        id="cluster:us-west",
        state="deploying",
        wave_id="wave:wave-1",
        bundle_id="bundle:web-services",
    )
    # Verify it's a single string, not a list
    assert isinstance(cluster.bundle_id, str)


def test_bundle_valid() -> None:
    """Test Bundle model with valid data."""
    bundle = Bundle(
        id="bundle:web-services",
        state="deploying",
        cluster_id="cluster:us-west",
        name="Web Services Bundle",
        app_ids=["app:api-gateway", "app:auth-service"],
    )
    assert bundle.id == "bundle:web-services"
    assert bundle.cluster_id == "cluster:us-west"
    assert len(bundle.app_ids) == 2


def test_app_valid() -> None:
    """Test App model with valid data."""
    app = App(
        id="app:api-gateway",
        state="running",
        bundle_id="bundle:web-services",
        name="API Gateway Service",
        version="v2.5.3",
    )
    assert app.id == "app:api-gateway"
    assert app.bundle_id == "bundle:web-services"
    assert app.version == "v2.5.3"


def test_app_invalid_bundle_id() -> None:
    """Test App rejects invalid Bundle ID."""
    with pytest.raises(ValidationError):
        App(
            id="app:api-gateway",
            state="running",
            bundle_id="invalid:bundle",  # Wrong format
        )


def test_entity_timestamps() -> None:
    """Test entity timestamp validation."""
    now = datetime.utcnow()
    release = Release(
        id="release:test-001",
        state="in_progress",
        workflow_id="wf_test",
        created_at=now,
        updated_at=now,
    )
    assert release.created_at == now
    assert release.updated_at == now


def test_entity_updated_at_validation() -> None:
    """Test updated_at must be >= created_at."""
    now = datetime.utcnow()
    with pytest.raises(ValidationError):
        Release(
            id="release:test-001",
            state="in_progress",
            workflow_id="wf_test",
            created_at=now,
            updated_at=datetime(2020, 1, 1),  # Earlier than created_at
        )


def test_release_hierarchy() -> None:
    """Test ReleaseHierarchy aggregate model."""
    hierarchy = ReleaseHierarchy(
        release=Release(
            id="release:test-001",
            state="in_progress",
            workflow_id="wf_test",
            wave_ids=["wave:wave-1"],
        ),
        waves=[],
    )
    assert hierarchy.release.id == "release:test-001"
    assert len(hierarchy.waves) == 0
