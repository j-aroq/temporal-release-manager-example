# Data Model: Temporal Release Management System

**Feature**: 001-temporal-bff-system
**Date**: 2025-11-06
**Purpose**: Define entities, their attributes, relationships, and validation rules

## Overview

This system manages a 5-level entity hierarchy representing deployment releases. All entities follow the ID format `entity-type:id` and are sourced from Temporal workflow state via query handlers.

**Important Cardinality Constraints**:
- Multiple releases can exist in the system
- Each release has **N Waves** (multiple waves per release)
- Each wave has **N Clusters** (multiple clusters per wave)
- Each cluster has exactly **1 Bundle** (single bundle per cluster)
- Each bundle has **N Apps** (multiple apps per bundle)

## Entity Hierarchy

```
Release (0..N multiple releases)
  └── Wave (N per release)
        └── Cluster (N per wave)
              └── Bundle (exactly 1 per cluster)
                    └── App (N per bundle)
```

**Simplified View**: Release → N Waves → N Clusters → 1 Bundle → N Apps

## Core Entities

### Release

**Description**: Top-level entity representing a deployment release. Corresponds to a Temporal workflow execution.

**Attributes**:
- `id` (string, required): Unique identifier formatted as "release:{id}"
  - Example: "release:rel-2025-01"
  - Validation: Must match pattern `^release:[a-zA-Z0-9_-]+$`
- `state` (string, required): Current state of the release
  - Examples: "pending", "in_progress", "completed", "failed"
  - Validation: Non-empty string, max 50 characters
- `workflow_id` (string, required): Temporal workflow execution ID
  - Used to query workflow for state
  - Validation: Non-empty string
- `created_at` (datetime, optional): When the release was created
  - ISO 8601 format
- `updated_at` (datetime, optional): When the release state was last updated
  - ISO 8601 format
- `wave_ids` (array of strings, optional): List of child Wave IDs
  - Each ID formatted as "wave:{id}"

**Relationships**:
- Parent: None (top-level, singleton)
- Children: 0 or more Waves, exactly 1 Bundle

**Cardinality**: Exactly 1 release exists at any time in the system

**State Transitions**: Defined by workflow logic (not enforced by BFF)

**Example**:
```json
{
  "id": "release:rel-2025-01",
  "state": "in_progress",
  "workflow_id": "wf_release_2025_01_abc123",
  "created_at": "2025-11-06T10:00:00Z",
  "updated_at": "2025-11-06T10:30:00Z",
  "wave_ids": ["wave:wave-1", "wave:wave-2"]
}
```

---

### Wave

**Description**: A deployment wave within a release. Represents a phase or batch in the release process.

**Attributes**:
- `id` (string, required): Unique identifier formatted as "wave:{id}"
  - Example: "wave:wave-1"
  - Validation: Must match pattern `^wave:[a-zA-Z0-9_-]+$`
- `state` (string, required): Current state of the wave
  - Examples: "pending", "deploying", "completed", "failed"
  - Validation: Non-empty string, max 50 characters
- `cluster_id` (string, required): Parent Cluster ID
  - Formatted as "cluster:{id}"
- `sequence` (integer, optional): Wave sequence number within release
  - Used for ordering waves (wave 1, wave 2, etc.)
- `created_at` (datetime, optional): When the wave was created
- `updated_at` (datetime, optional): When the wave state was last updated
- `cluster_ids` (array of strings, optional): List of child Cluster IDs

**Relationships**:
- Parent: Exactly 1 Release
- Children: 0 or more Clusters

**Cardinality**: Multiple waves can exist per release

**Example**:
```json
{
  "id": "wave:wave-1",
  "state": "deploying",
  "release_id": "release:rel-2025-01",
  "sequence": 1,
  "created_at": "2025-11-06T10:05:00Z",
  "updated_at": "2025-11-06T10:35:00Z",
  "cluster_ids": ["cluster:us-west", "cluster:us-east"]
}
```

---

### Cluster

**Description**: A deployment cluster within a wave. Represents a logical grouping of deployment targets.

**Attributes**:
- `id` (string, required): Unique identifier formatted as "cluster:{id}"
  - Example: "cluster:us-west"
  - Validation: Must match pattern `^cluster:[a-zA-Z0-9_-]+$`
- `state` (string, required): Current state of the cluster
  - Examples: "pending", "deploying", "completed", "failed"
  - Validation: Non-empty string, max 50 characters
- `wave_id` (string, required): Parent Wave ID
  - Formatted as "wave:{id}"
- `name` (string, optional): Human-readable cluster name
  - Example: "US West Production"
- `created_at` (datetime, optional): When the cluster was created
- `updated_at` (datetime, optional): When the cluster state was last updated
- `bundle_id` (string, optional): Child Bundle ID (exactly one per cluster)
  - Formatted as "bundle:{id}"

**Relationships**:
- Parent: Exactly 1 Wave
- Children: Exactly 1 Bundle

**Cardinality**: Each cluster contains exactly 1 bundle

**Example**:
```json
{
  "id": "cluster:us-west",
  "state": "deploying",
  "wave_id": "wave:wave-1",
  "name": "US West Production",
  "created_at": "2025-11-06T10:10:00Z",
  "updated_at": "2025-11-06T10:40:00Z",
  "bundle_id": "bundle:web-services"
}
```

---

### Bundle

**Description**: A deployment bundle within a cluster. Represents a package of applications to be deployed together.

**Attributes**:
- `id` (string, required): Unique identifier formatted as "bundle:{id}"
  - Example: "bundle:web-services"
  - Validation: Must match pattern `^bundle:[a-zA-Z0-9_-]+$`
- `state` (string, required): Current state of the bundle
  - Examples: "pending", "deploying", "completed", "failed"
  - Validation: Non-empty string, max 50 characters
- `cluster_id` (string, required): Parent Cluster ID
  - Formatted as "cluster:{id}"
- `name` (string, optional): Human-readable bundle name
  - Example: "Web Services Bundle"
- `created_at` (datetime, optional): When the bundle was created
- `updated_at` (datetime, optional): When the bundle state was last updated
- `app_ids` (array of strings, optional): List of child App IDs

**Relationships**:
- Parent: Exactly 1 Cluster
- Children: 0 or more Apps

**Cardinality**: Exactly 1 bundle per cluster

**Example**:
```json
{
  "id": "bundle:web-services",
  "state": "deploying",
  "cluster_id": "cluster:us-west",
  "name": "Web Services Bundle",
  "created_at": "2025-11-06T10:15:00Z",
  "updated_at": "2025-11-06T10:45:00Z",
  "app_ids": ["app:api-gateway", "app:auth-service", "app:user-service"]
}
```

---

### App

**Description**: An individual application within a bundle. The leaf node in the hierarchy - the actual application being deployed.

**Attributes**:
- `id` (string, required): Unique identifier formatted as "app:{id}"
  - Example: "app:api-gateway"
  - Validation: Must match pattern `^app:[a-zA-Z0-9_-]+$`
- `state` (string, required): Current state of the app
  - Examples: "pending", "deploying", "running", "failed", "stopped"
  - Validation: Non-empty string, max 50 characters
- `bundle_id` (string, required): Parent Bundle ID
  - Formatted as "bundle:{id}"
- `name` (string, optional): Human-readable app name
  - Example: "API Gateway Service"
- `version` (string, optional): App version being deployed
  - Example: "v2.5.3"
- `created_at` (datetime, optional): When the app deployment started
- `updated_at` (datetime, optional): When the app state was last updated

**Relationships**:
- Parent: Exactly 1 Bundle
- Children: None (leaf node)

**Example**:
```json
{
  "id": "app:api-gateway",
  "state": "running",
  "bundle_id": "bundle:web-services",
  "name": "API Gateway Service",
  "version": "v2.5.3",
  "created_at": "2025-11-06T10:20:00Z",
  "updated_at": "2025-11-06T10:50:00Z"
}
```

---

## Supporting Entities

### User

**Description**: A person accessing the release management system.

**Attributes**:
- `id` (string, required): Unique user identifier
  - UUID format
- `email` (string, required): User email address
  - Validation: Valid email format
  - Used for login
- `hashed_password` (string, required): Bcrypt-hashed password
  - Never exposed in API responses
- `full_name` (string, optional): User's full name
- `is_active` (boolean, required): Whether user account is active
  - Default: true
- `is_admin` (boolean, required): Whether user has admin privileges
  - Default: false
- `created_at` (datetime, required): Account creation timestamp
- `last_login` (datetime, optional): Last successful login timestamp

**Validation Rules**:
- Email must be unique
- Password must be at least 8 characters (enforced on registration, not stored)

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-11-01T09:00:00Z",
  "last_login": "2025-11-06T08:30:00Z"
}
```

---

### Token

**Description**: JWT authentication token.

**Attributes**:
- `access_token` (string, required): JWT token string
- `token_type` (string, required): Always "bearer"
- `expires_in` (integer, optional): Token expiration time in seconds

**Example**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Aggregate Models

### ReleaseHierarchy

**Description**: Complete release with all nested children loaded.

**Structure**:
```json
{
  "release": {Release},
  "waves": [
    {
      "wave": {Wave},
      "clusters": [
        {
          "cluster": {Cluster},
          "bundles": [
            {
              "bundle": {Bundle},
              "apps": [{App}, {App}, ...]
            },
            ...
          ]
        },
        ...
      ]
    },
    ...
  ]
}
```

**Use Case**: Release detail page displaying full hierarchy

---

## Validation Rules

### ID Format Validation

All entity IDs must follow the pattern: `{entity-type}:{identifier}`

**Valid Examples**:
- `release:rel-2025-01`
- `wave:wave-1`
- `cluster:us-west-prod`
- `bundle:web-bundle-v2`
- `app:api-gateway-service`

**Invalid Examples**:
- `release123` (missing colon)
- `rel:release-123` (wrong type)
- `release:` (empty identifier)
- `release:has spaces` (contains spaces)

**Regex Pattern**: `^(release|wave|cluster|bundle|app):[a-zA-Z0-9_-]+$`

### State Validation

- States are case-sensitive strings
- Maximum length: 50 characters
- Must be non-empty
- Common states (not exhaustive):
  - `pending`: Entity created, not yet started
  - `in_progress` / `deploying`: Active operation
  - `completed` / `running`: Successfully finished
  - `failed`: Operation failed
  - `stopped`: Intentionally stopped

### Relationship Integrity

- Every child entity MUST have exactly one valid parent ID
- Parent ID must reference an existing entity of the correct type
- Orphaned entities (parent not found) should be handled gracefully with errors

### Timestamp Validation

- All timestamps in ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
- `updated_at` must be >= `created_at` when both present
- Timestamps are optional but recommended for audit trails

---

## Data Flow

### From Temporal to BFF

1. **Workflow Query**: BFF queries Temporal workflow using workflow_id
2. **State Extraction**: Workflow query handler returns entity state as JSON
3. **Deserialization**: BFF deserializes JSON into Pydantic models
4. **Validation**: Pydantic validates data against schema rules
5. **API Response**: Validated models serialized to JSON for API response

### Hierarchy Construction

1. Query parent entity (e.g., Release)
2. Extract child IDs from parent (e.g., wave_ids)
3. Fan-out parallel queries for all children
4. Recursively repeat for each child level
5. Assemble complete hierarchy tree

---

## Pydantic Model Guidelines

**Base Model Pattern**:
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

class EntityBase(BaseModel):
    id: str = Field(..., pattern=r'^(release|wave|cluster|bundle|app):[a-zA-Z0-9_-]+$')
    state: str = Field(..., max_length=50, min_length=1)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Validation**:
- Use Pydantic `Field` for constraints (max_length, pattern, etc.)
- Use `@validator` decorators for complex validation logic
- Raise `ValueError` with clear messages for validation failures

**Serialization**:
- Pydantic models auto-serialize to JSON
- Use `.dict()` for dictionary representation
- Use `.json()` for JSON string representation

---

## Error Cases

### Not Found

**Scenario**: Entity ID does not correspond to an existing workflow or entity.

**Response**: 404 with clear message
```json
{
  "detail": "Release not found: release:rel-999. It may have been completed or removed."
}
```

### Malformed ID

**Scenario**: ID does not match required format.

**Response**: 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "id"],
      "msg": "ID must match pattern: {entity-type}:{identifier}",
      "type": "value_error.str.regex"
    }
  ]
}
```

### Workflow Query Failure

**Scenario**: Temporal is unreachable or workflow query times out.

**Response**: 503 Service Unavailable
```json
{
  "detail": "Unable to query workflow state. Please try again later."
}
```

---

## Summary

The data model centers on a strict 5-level hierarchy (Release → Wave → Cluster → Bundle → App) with:
- Standardized ID format (`entity-type:id`)
- State tracking at every level
- Parent-child relationships
- Validation rules enforced via Pydantic
- Data sourced from Temporal workflow queries
- Clear error handling for edge cases

All entities are read-only from the BFF perspective - state changes occur only in Temporal workflows.
