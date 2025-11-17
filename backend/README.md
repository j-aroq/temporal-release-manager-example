# Temporal Release Management Backend

Backend for Frontend (BFF) system for querying Temporal workflow state to display deployment release hierarchies.

## Features

- **FastAPI-based REST API** for release state queries
- **Temporal Python SDK integration** for workflow queries
- **JWT authentication** with secure password hashing
- **Pydantic models** for data validation
- **Async/await** for high performance
- **Comprehensive test suite** (unit, integration, contract tests)

## Prerequisites

- **Python 3.11+**
- **Temporal CLI** installed locally (see [Temporal installation guide](https://docs.temporal.io/cli))
- **pip** or **poetry** for dependency management

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set required variables (especially JWT_SECRET)
# Generate a secure JWT_SECRET with:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start Temporal Server

In a separate terminal:

```bash
# Start Temporal development server
temporal server start-dev

# This starts:
# - Temporal Server (localhost:7233)
# - Temporal UI (http://localhost:8080)
```

### 4. Run the Backend

```bash
# Start the API server with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: http://localhost:8000/api
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m contract      # API contract tests only

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_entities.py
```

### Code Quality

```bash
# Format code with black
black src tests

# Lint with ruff
ruff check src tests

# Type checking with mypy
mypy src

# Run pylint
pylint src
```

### Project Structure

```
backend/
├── src/
│   ├── api/              # FastAPI routes and endpoints
│   │   ├── __init__.py
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── releases.py   # Release endpoints
│   │   └── entities.py   # Entity query endpoints
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   ├── temporal_client.py  # Temporal workflow queries
│   │   ├── auth_service.py     # Authentication logic
│   │   └── entity_service.py   # Entity retrieval
│   ├── models/           # Pydantic data models
│   │   ├── __init__.py
│   │   ├── entities.py   # Release, Wave, Cluster, Bundle, App
│   │   └── auth.py       # User, Token models
│   ├── core/             # Configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py     # Settings management
│   │   ├── security.py   # JWT, password hashing
│   │   └── logging.py    # Structured logging
│   └── main.py           # FastAPI application
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── contract/         # API contract tests
├── pyproject.toml        # Dependencies and configuration
├── .env.example          # Example environment variables
└── README.md             # This file
```

## API Endpoints

### Authentication

- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Releases

- `GET /api/releases` - List all releases (paginated)
- `GET /api/releases/{release_id}` - Get release details
- `GET /api/releases/{release_id}/hierarchy` - Get full release hierarchy

### Entities

- `GET /api/entities/{entity_id}` - Get individual entity state

## Authentication

All endpoints (except `/auth/login`) require JWT authentication.

### Getting a Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

### Using the Token

```bash
curl http://localhost:8000/api/releases \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Default User (Development Only)

- **Email**: `admin@example.com`
- **Password**: `admin123`

## Entity Hierarchy

```
Release (N)
  └── Wave (N per release)
        └── Cluster (N per wave)
              └── Bundle (1 per cluster)
                    └── App (N per bundle)
```

### Entity ID Format

All entity IDs follow the pattern: `{entity-type}:{identifier}`

Examples:
- `release:rel-2025-01`
- `wave:wave-1`
- `cluster:us-west`
- `bundle:web-services`
- `app:api-gateway`

## Configuration

See `.env.example` for all available configuration options.

Key variables:
- `TEMPORAL_HOST` - Temporal server address
- `JWT_SECRET` - Secret for JWT token signing (required)
- `API_CORS_ORIGINS` - Allowed CORS origins
- `LOG_LEVEL` - Logging verbosity

## Troubleshooting

### Backend won't start

**Check Temporal is running**:
```bash
# Temporal UI should be accessible
curl http://localhost:8080
```

**Check environment variables**:
```bash
# Ensure .env file exists and JWT_SECRET is set
cat .env | grep JWT_SECRET
```

**Check port availability**:
```bash
# Ensure port 8000 is not in use
lsof -i :8000
```

### Authentication fails

**Verify JWT_SECRET is set**:
```bash
grep JWT_SECRET .env
```

**Check user credentials**: Default user is `admin@example.com` / `admin123`

### Temporal connection errors

**Ensure Temporal is running**: Visit http://localhost:8080

**Check TEMPORAL_HOST**: Should be `localhost:7233` for local development

## Production Deployment

1. **Set secure JWT_SECRET**: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. **Configure production Temporal**: Update `TEMPORAL_HOST` to production cluster
3. **Set CORS origins**: Limit `API_CORS_ORIGINS` to production domain
4. **Disable debug mode**: Set `DEBUG=false`
5. **Configure logging**: Set appropriate `LOG_LEVEL`
6. **Use HTTPS**: Deploy behind reverse proxy (nginx, Traefik)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Temporal Python SDK](https://docs.temporal.io/dev-guide/python)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)

## Support

For issues or questions:
1. Check API documentation at http://localhost:8000/docs
2. Review backend logs for errors
3. Consult spec and architecture docs in `specs/001-temporal-bff-system/`
4. File an issue if problem persists
