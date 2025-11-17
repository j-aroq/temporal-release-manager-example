# Temporal Release Management System

Backend for Frontend (BFF) system that queries Temporal workflows to display deployment release states through a web dashboard and REST API.

## Overview

This system tracks a 5-level entity hierarchy (Release → Wave → Cluster → Bundle → App) where each entity has an ID and state exposed via Temporal query handlers. The frontend uses React with Chakra UI, and the backend uses FastAPI with the Temporal Python SDK.

## Quick Start

Get the system running locally in under 10 minutes. See [quickstart.md](specs/001-temporal-bff-system/quickstart.md) for detailed instructions.

### 🧪 **NEW: Testing with Sample Data**

Want to see the system in action immediately? See **[TESTING.md](TESTING.md)** for a complete guide including:
- ✅ Step-by-step setup (5 minutes)
- ✅ Sample workflow generator
- ✅ Test scenarios and verification
- ✅ Troubleshooting guide

**Quick test workflow:**
```bash
# Terminal 1: Start Temporal
temporal server start-dev

# Terminal 2: Start Backend
cd backend && source venv/bin/activate && uvicorn src.main:app --reload

# Terminal 3: Start Frontend
cd frontend && npm start

# Terminal 4: Start Worker
cd backend && source venv/bin/activate && python worker.py

# Terminal 5: Create Test Data
cd backend && source venv/bin/activate && python test_workflows.py
```

Then open http://localhost:3000 and login with `admin@example.com` / `admin123`!

### Prerequisites

- **Temporal CLI** - Install locally (not Docker): [Installation Guide](https://docs.temporal.io/cli)
  ```bash
  # macOS
  brew install temporal

  # Or download from https://docs.temporal.io/cli
  ```
- **Python 3.11+** - For backend
- **Node.js 18+** - For frontend
- **Git** - For version control

### Local Development Setup

You need **3 terminals running**:

**Terminal 1 - Temporal Server**:
```bash
# Start Temporal development server
temporal server start-dev

# Access Temporal UI at http://localhost:8080
```

**Terminal 2 - Backend API**:
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env and set JWT_SECRET (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")

# Start backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend Dashboard**:
```bash
cd frontend

# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env

# Start frontend
npm start
```

### Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8080
- **API Health Check**: http://localhost:8000/health

### Default Login (Development)

- **Email**: `admin@example.com`
- **Password**: `admin123`

## Project Structure

```
bff-temporal/
├── backend/                # FastAPI backend
│   ├── src/
│   │   ├── api/           # REST API endpoints
│   │   ├── services/      # Business logic & Temporal client
│   │   ├── models/        # Pydantic data models
│   │   └── core/          # Configuration & utilities
│   ├── tests/             # Backend tests
│   └── pyproject.toml     # Python dependencies
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page-level components
│   │   ├── services/      # API client services
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript types
│   ├── tests/             # Frontend tests
│   └── package.json       # Node dependencies
├── specs/                 # Feature specifications
│   └── 001-temporal-bff-system/
│       ├── spec.md        # Feature specification
│       ├── plan.md        # Implementation plan
│       ├── data-model.md  # Entity definitions
│       ├── research.md    # Technical decisions
│       ├── tasks.md       # Implementation tasks
│       ├── quickstart.md  # Quick start guide
│       └── contracts/     # API contracts (OpenAPI)
└── README.md              # This file
```

## Entity Hierarchy

```
Release (N releases can exist)
  └── Wave (N waves per release)
        └── Cluster (N clusters per wave)
              └── Bundle (exactly 1 bundle per cluster)
                    └── App (N apps per bundle)
```

### Entity ID Format

All entities use the format: `{entity-type}:{id}`

**Examples**:
- `release:rel-2025-01`
- `wave:wave-1`
- `cluster:us-west`
- `bundle:web-services`
- `app:api-gateway`

## Key Features

- ✅ **JWT Authentication** - Secure access to release information
- ✅ **Release List View** - Browse all active releases
- ✅ **Release Detail View** - Drill down into complete entity hierarchy
- ✅ **REST API** - Programmatic access to release and entity states
- ✅ **Real-time Updates** - Automatic polling for state changes (configurable)
- ✅ **Temporal Integration** - Direct queries to workflow state (no separate database)

## User Stories

1. **US1 (P1)** - View Release List - See all releases on main page
2. **US2 (P1)** - Navigate to Release Details - Click release to view hierarchy
3. **US3 (P2)** - Query Entity States via API - Programmatic access
4. **US4 (P1)** - Authentication - Secure access to release information
5. **US5 (P3)** - Real-time State Updates - Auto-refresh without manual reload

## Architecture

### Backend (FastAPI + Temporal)

- **FastAPI** - Async REST API framework
- **Temporal Python SDK** - Workflow query client
- **Pydantic** - Data validation and serialization
- **JWT Authentication** - Stateless token-based auth
- **Parallel Queries** - Async fan-out for fast hierarchy retrieval

### Frontend (React + Chakra UI)

- **React 18** - Component-based UI framework
- **Chakra UI** - Accessible component library
- **TypeScript** - Type-safe development
- **React Router** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Polling** - Real-time state updates (3-5 second interval)

### Data Flow

```
┌─────────────┐
│   Browser   │
│  (React +   │
│  Chakra UI) │ ← User views dashboard
└──────┬──────┘
       │ HTTP/REST
       ↓
┌──────────────┐
│   FastAPI    │
│   Backend    │ ← BFF queries workflows
│     (BFF)    │
└──────┬───────┘
       │ Temporal Query
       ↓
┌──────────────┐
│   Temporal   │
│   Workflows  │ ← Source of truth for state
└──────────────┘
```

## Development Workflow

### Running Tests

**Backend**:
```bash
cd backend
pytest                    # All tests
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest --cov             # With coverage
```

**Frontend**:
```bash
cd frontend
npm test                 # Unit tests
npm run test:coverage    # With coverage
npm run test:e2e         # E2E tests
```

### Code Quality

**Backend**:
```bash
cd backend
black src tests          # Format code
ruff check src tests     # Lint
mypy src                 # Type checking
pylint src               # Additional linting
```

**Frontend**:
```bash
cd frontend
npm run lint             # Lint TypeScript
npm run format           # Format code
npm run type-check       # Type checking
```

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Example API Requests

**Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@example.com&password=admin123"
```

**List Releases**:
```bash
curl http://localhost:8000/api/releases \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Release Hierarchy**:
```bash
curl http://localhost:8000/api/releases/release:rel-001/hierarchy \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Configuration

### Backend (.env)

Key variables:
- `TEMPORAL_HOST=localhost:7233` - Temporal server address
- `JWT_SECRET=<secure-random-string>` - Token signing secret (required)
- `API_CORS_ORIGINS=["http://localhost:3000"]` - Allowed CORS origins
- `LOG_LEVEL=INFO` - Logging verbosity

### Frontend (.env)

Key variables:
- `REACT_APP_API_URL=http://localhost:8000/api` - Backend API URL
- `REACT_APP_POLLING_INTERVAL=3000` - State update polling interval (ms)

## Troubleshooting

### Backend won't start

1. **Check Temporal is running**: Open http://localhost:8080
2. **Verify environment variables**: Ensure `.env` exists with `JWT_SECRET`
3. **Check port availability**: Run `lsof -i :8000`
4. **Check Python version**: Run `python --version` (should be 3.11+)

### Frontend won't connect

1. **Verify backend is running**: Run `curl http://localhost:8000/health`
2. **Check CORS configuration**: Backend must allow frontend origin
3. **Verify API URL**: Check `REACT_APP_API_URL` in `.env`

### Authentication fails

1. **Check JWT_SECRET is set**: Run `grep JWT_SECRET backend/.env`
2. **Verify default user credentials**: `admin@example.com` / `admin123`
3. **Check backend logs**: Look for authentication errors

### No releases showing

1. **Check Temporal workflows**: Open http://localhost:8080 - any workflows running?
2. **Verify workflow query handlers**: Workflows must expose query handlers
3. **Check backend logs**: Look for Temporal connection errors

## Production Deployment

See detailed deployment guide in `specs/001-temporal-bff-system/quickstart.md`.

**Key Steps**:
1. Generate secure `JWT_SECRET`
2. Configure production Temporal cluster
3. Enable HTTPS (reverse proxy)
4. Set production CORS origins
5. Configure structured logging
6. Set up monitoring and metrics

## Documentation

- **Feature Spec**: [specs/001-temporal-bff-system/spec.md](specs/001-temporal-bff-system/spec.md)
- **Implementation Plan**: [specs/001-temporal-bff-system/plan.md](specs/001-temporal-bff-system/plan.md)
- **Data Model**: [specs/001-temporal-bff-system/data-model.md](specs/001-temporal-bff-system/data-model.md)
- **API Contracts**: [specs/001-temporal-bff-system/contracts/](specs/001-temporal-bff-system/contracts/)
- **Quick Start**: [specs/001-temporal-bff-system/quickstart.md](specs/001-temporal-bff-system/quickstart.md)
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)

## Resources

- **Temporal Docs**: https://docs.temporal.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Chakra UI Docs**: https://chakra-ui.com/

## Project Constitution

This project follows strict development principles defined in `.specify/memory/constitution.md`:

- ✅ Zero tolerance for technical debt
- ✅ No version fragmentation (no v1/v2/v3)
- ✅ Simplicity first (YAGNI, KISS, SOLID)
- ✅ Test-Driven Development (TDD mandatory)
- ✅ Root cause fixes only (no workarounds)
- ✅ Context-aware development
- ✅ Code hygiene (delete unused code, report overengineering)

## License

MIT

## Support

For issues or questions:
1. Check documentation in `specs/001-temporal-bff-system/`
2. Review backend and frontend READMEs
3. Check Temporal UI for workflow status
4. Review application logs for errors
5. File an issue if problem persists
