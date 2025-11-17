"""
Pydantic models for release management entities.

Defines the 5-level entity hierarchy:
Release → Wave → Cluster → Bundle → App
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# Entity ID validation pattern
ENTITY_ID_PATTERN = r"^(release|wave|cluster|bundle|app):[a-zA-Z0-9_-]+$"


class EntityBase(BaseModel):
    """Base model for all entities with common fields."""

    id: str = Field(..., pattern=ENTITY_ID_PATTERN, description="Entity ID in format type:id")
    state: str = Field(..., min_length=1, max_length=50, description="Current entity state")
    created_at: Optional[datetime] = Field(None, description="Entity creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last state update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "release:rel-2025-01",
                "state": "in_progress",
                "created_at": "2025-11-06T10:00:00Z",
                "updated_at": "2025-11-06T10:30:00Z",
            }
        }
    }

    @field_validator("updated_at")
    @classmethod
    def validate_updated_at(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Validate that updated_at is >= created_at if both present."""
        if v and "created_at" in info.data and info.data["created_at"]:
            if v < info.data["created_at"]:
                raise ValueError("updated_at must be >= created_at")
        return v


class Release(EntityBase):
    """
    Release entity - top level in hierarchy.

    Represents a deployment release tracked by a Temporal workflow.
    """

    workflow_id: str = Field(..., description="Temporal workflow execution ID")
    wave_ids: List[str] = Field(
        default_factory=list, description="List of child Wave IDs (wave:id format)"
    )

    @field_validator("id")
    @classmethod
    def validate_release_id(cls, v: str) -> str:
        """Validate ID starts with 'release:'."""
        if not v.startswith("release:"):
            raise ValueError("Release ID must start with 'release:'")
        return v

    @field_validator("wave_ids")
    @classmethod
    def validate_wave_ids(cls, v: List[str]) -> List[str]:
        """Validate all wave IDs start with 'wave:'."""
        for wave_id in v:
            if not wave_id.startswith("wave:"):
                raise ValueError(f"Wave ID must start with 'wave:', got: {wave_id}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "release:rel-2025-01",
                "state": "in_progress",
                "workflow_id": "wf_release_2025_01_abc123",
                "created_at": "2025-11-06T10:00:00Z",
                "updated_at": "2025-11-06T10:30:00Z",
                "wave_ids": ["wave:wave-1", "wave:wave-2"],
            }
        }
    }


class Wave(EntityBase):
    """
    Wave entity - second level in hierarchy.

    Represents a deployment wave within a release.
    """

    release_id: str = Field(..., pattern=r"^release:[a-zA-Z0-9_-]+$", description="Parent Release ID")
    sequence: Optional[int] = Field(None, ge=1, description="Wave sequence number")
    cluster_ids: List[str] = Field(
        default_factory=list, description="List of child Cluster IDs (cluster:id format)"
    )

    @field_validator("id")
    @classmethod
    def validate_wave_id(cls, v: str) -> str:
        """Validate ID starts with 'wave:'."""
        if not v.startswith("wave:"):
            raise ValueError("Wave ID must start with 'wave:'")
        return v

    @field_validator("cluster_ids")
    @classmethod
    def validate_cluster_ids(cls, v: List[str]) -> List[str]:
        """Validate all cluster IDs start with 'cluster:'."""
        for cluster_id in v:
            if not cluster_id.startswith("cluster:"):
                raise ValueError(f"Cluster ID must start with 'cluster:', got: {cluster_id}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "wave:wave-1",
                "state": "deploying",
                "release_id": "release:rel-2025-01",
                "sequence": 1,
                "created_at": "2025-11-06T10:05:00Z",
                "updated_at": "2025-11-06T10:35:00Z",
                "cluster_ids": ["cluster:us-west", "cluster:us-east"],
            }
        }
    }


class Cluster(EntityBase):
    """
    Cluster entity - third level in hierarchy.

    Represents a deployment cluster within a wave.
    Each cluster contains exactly 1 bundle.
    """

    wave_id: str = Field(..., pattern=r"^wave:[a-zA-Z0-9_-]+$", description="Parent Wave ID")
    name: Optional[str] = Field(None, description="Human-readable cluster name")
    bundle_id: Optional[str] = Field(
        None, pattern=r"^bundle:[a-zA-Z0-9_-]+$", description="Child Bundle ID (exactly 1 per cluster)"
    )

    @field_validator("id")
    @classmethod
    def validate_cluster_id(cls, v: str) -> str:
        """Validate ID starts with 'cluster:'."""
        if not v.startswith("cluster:"):
            raise ValueError("Cluster ID must start with 'cluster:'")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "cluster:us-west",
                "state": "deploying",
                "wave_id": "wave:wave-1",
                "name": "US West Production",
                "created_at": "2025-11-06T10:10:00Z",
                "updated_at": "2025-11-06T10:40:00Z",
                "bundle_id": "bundle:web-services",
            }
        }
    }


class Bundle(EntityBase):
    """
    Bundle entity - fourth level in hierarchy.

    Represents a deployment bundle within a cluster.
    Exactly 1 bundle per cluster.
    """

    cluster_id: str = Field(..., pattern=r"^cluster:[a-zA-Z0-9_-]+$", description="Parent Cluster ID")
    name: Optional[str] = Field(None, description="Human-readable bundle name")
    app_ids: List[str] = Field(
        default_factory=list, description="List of child App IDs (app:id format)"
    )

    @field_validator("id")
    @classmethod
    def validate_bundle_id(cls, v: str) -> str:
        """Validate ID starts with 'bundle:'."""
        if not v.startswith("bundle:"):
            raise ValueError("Bundle ID must start with 'bundle:'")
        return v

    @field_validator("app_ids")
    @classmethod
    def validate_app_ids(cls, v: List[str]) -> List[str]:
        """Validate all app IDs start with 'app:'."""
        for app_id in v:
            if not app_id.startswith("app:"):
                raise ValueError(f"App ID must start with 'app:', got: {app_id}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "bundle:web-services",
                "state": "deploying",
                "cluster_id": "cluster:us-west",
                "name": "Web Services Bundle",
                "created_at": "2025-11-06T10:15:00Z",
                "updated_at": "2025-11-06T10:45:00Z",
                "app_ids": ["app:api-gateway", "app:auth-service", "app:user-service"],
            }
        }
    }


class App(EntityBase):
    """
    App entity - fifth (leaf) level in hierarchy.

    Represents an individual application within a bundle.
    """

    bundle_id: str = Field(..., pattern=r"^bundle:[a-zA-Z0-9_-]+$", description="Parent Bundle ID")
    name: Optional[str] = Field(None, description="Human-readable app name")
    version: Optional[str] = Field(None, description="App version being deployed")

    @field_validator("id")
    @classmethod
    def validate_app_id(cls, v: str) -> str:
        """Validate ID starts with 'app:'."""
        if not v.startswith("app:"):
            raise ValueError("App ID must start with 'app:'")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "app:api-gateway",
                "state": "running",
                "bundle_id": "bundle:web-services",
                "name": "API Gateway Service",
                "version": "v2.5.3",
                "created_at": "2025-11-06T10:20:00Z",
                "updated_at": "2025-11-06T10:50:00Z",
            }
        }
    }


# Aggregate models for hierarchical responses


class BundleWithApps(BaseModel):
    """Bundle with its child apps."""

    bundle: Bundle
    apps: List[App] = Field(default_factory=list)


class ClusterWithBundles(BaseModel):
    """Cluster with its child bundle (exactly 1) and apps."""

    cluster: Cluster
    bundles: List[BundleWithApps] = Field(default_factory=list)


class WaveWithClusters(BaseModel):
    """Wave with its child clusters, bundles, and apps."""

    wave: Wave
    clusters: List[ClusterWithBundles] = Field(default_factory=list)


class ReleaseHierarchy(BaseModel):
    """
    Complete release hierarchy with all nested entities.

    Simplified structure matching workflow output:
    {
        id, state, workflow_id, created_at, updated_at, wave_ids,
        waves: [
            {id, state, ..., clusters: [
                {id, state, ..., bundle: {id, state, ..., apps: [...]}}
            ]}
        ]
    }
    """
    # Release-level fields
    id: str
    state: str
    workflow_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    wave_ids: List[str] = Field(default_factory=list)

    # Nested hierarchy - accept as dict to allow any structure
    waves: List[dict] = Field(default_factory=list)

    model_config = {
        "extra": "allow",  # Allow additional fields from workflow
    }

    model_config = {
        "json_schema_extra": {
            "example": {
                "release": {
                    "id": "release:rel-2025-01",
                    "state": "in_progress",
                    "workflow_id": "wf_release_2025_01_abc123",
                    "wave_ids": ["wave:wave-1"],
                },
                "waves": [
                    {
                        "wave": {
                            "id": "wave:wave-1",
                            "state": "deploying",
                            "release_id": "release:rel-2025-01",
                            "cluster_ids": ["cluster:us-west"],
                        },
                        "clusters": [
                            {
                                "cluster": {
                                    "id": "cluster:us-west",
                                    "state": "deploying",
                                    "wave_id": "wave:wave-1",
                                    "bundle_id": "bundle:web-services",
                                },
                                "bundles": [
                                    {
                                        "bundle": {
                                            "id": "bundle:web-services",
                                            "state": "deploying",
                                            "cluster_id": "cluster:us-west",
                                            "app_ids": ["app:api-gateway"],
                                        },
                                        "apps": [
                                            {
                                                "id": "app:api-gateway",
                                                "state": "running",
                                                "bundle_id": "bundle:web-services",
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        }
    }
