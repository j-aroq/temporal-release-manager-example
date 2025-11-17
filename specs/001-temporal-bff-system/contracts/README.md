# API Contracts

This directory contains the API contract specifications for the Temporal Release Management System.

## Files

- **api.openapi.yaml**: OpenAPI 3.0 specification for the REST API

## API Overview

### Base URL

- Development: `http://localhost:8000/api`
- Production: `https://api.example.com/api`

### Authentication

All endpoints (except `/auth/login`) require JWT Bearer authentication.

**Get Token**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=mypassword"
```

**Use Token**:
```bash
curl http://localhost:8000/api/releases \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Endpoints

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |

### Releases

| Method | Path | Description |
|--------|------|-------------|
| GET | `/releases` | List all releases (paginated) |
| GET | `/releases/{release_id}` | Get release details |
| GET | `/releases/{release_id}/hierarchy` | Get full release hierarchy |

### Entities

| Method | Path | Description |
|--------|------|-------------|
| GET | `/entities/{entity_id}` | Get individual entity state |

## Examples

### List Releases

```bash
curl http://localhost:8000/api/releases \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "items": [
    {
      "id": "release:rel-2025-01",
      "state": "in_progress",
      "workflow_id": "wf_release_2025_01_abc123",
      "created_at": "2025-11-06T10:00:00Z",
      "updated_at": "2025-11-06T10:30:00Z",
      "wave_ids": ["wave:wave-1", "wave:wave-2"]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### Get Release Hierarchy

```bash
curl http://localhost:8000/api/releases/release:rel-2025-01/hierarchy \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response (truncated):
```json
{
  "release": {
    "id": "release:rel-2025-01",
    "state": "in_progress",
    ...
  },
  "waves": [
    {
      "wave": {
        "id": "wave:wave-1",
        "state": "deploying",
        ...
      },
      "clusters": [
        {
          "cluster": {
            "id": "cluster:us-west",
            "state": "deploying",
            ...
          },
          "bundles": [
            {
              "bundle": {
                "id": "bundle:web-services",
                "state": "deploying",
                ...
              },
              "apps": [
                {
                  "id": "app:api-gateway",
                  "state": "running",
                  ...
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Query Individual Entity

```bash
curl http://localhost:8000/api/entities/app:api-gateway \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
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

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found

```json
{
  "detail": "Release not found: release:rel-999. It may have been completed or removed."
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["path", "release_id"],
      "msg": "string does not match regex",
      "type": "value_error.str.regex"
    }
  ]
}
```

### 503 Service Unavailable

```json
{
  "detail": "Unable to query workflow state. Please try again later."
}
```

## Entity ID Formats

All entity IDs follow the pattern: `{entity-type}:{identifier}`

**Valid Examples**:
- `release:rel-2025-01`
- `wave:wave-1`
- `cluster:us-west`
- `bundle:web-services`
- `app:api-gateway`

**Regex**: `^(release|wave|cluster|bundle|app):[a-zA-Z0-9_-]+$`

## Validation

Validate API responses against the OpenAPI schema using tools like:
- [openapi-cli](https://github.com/Redocly/openapi-cli)
- [swagger-cli](https://github.com/APIDevTools/swagger-cli)
- [Prism](https://github.com/stoplightio/prism)

## Interactive Documentation

When the backend server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

FastAPI automatically generates interactive API documentation from the OpenAPI schema.
