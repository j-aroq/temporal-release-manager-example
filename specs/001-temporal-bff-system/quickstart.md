# Quickstart: Temporal Release Management System

**Feature**: 001-temporal-bff-system
**Date**: 2025-11-06
**Purpose**: Get the system running locally in under 10 minutes

## Prerequisites

- **Temporal Server** installed locally (see https://docs.temporal.io/cli)
- **Python 3.11+** for backend
- **Node.js 18+** for frontend
- **Git**

## Quick Start (Local Development)

Get the system running with local Temporal installation:

### 1. Install Temporal CLI

Follow the official Temporal installation guide:
```bash
# macOS (using Homebrew)
brew install temporal

# Or download from https://docs.temporal.io/cli
```

### 2. Start Temporal Server

```bash
# Start Temporal development server
temporal server start-dev

# This starts:
# - Temporal Server (localhost:7233)
# - Temporal UI (http://localhost:8080)
```

Keep this terminal running.

### 3. Clone and Navigate

In a new terminal:
```bash
git clone <repository-url>
cd bff-temporal
git checkout 001-temporal-bff-system
```

### 4. Configure Environment

Create `.env` file in project root:

```bash
# Backend configuration
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
JWT_SECRET=your-secret-key-change-this-in-production
JWT_EXPIRE_MINUTES=30
API_CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO

# Frontend configuration
REACT_APP_API_URL=http://localhost:8000/api
```

**IMPORTANT**: Change `JWT_SECRET` to a random secure value for production!

### 5. Start Backend

In a new terminal:
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start Frontend

In another new terminal:
```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

### 7. Verify Services

```bash
# Check Temporal UI
open http://localhost:8080

# Check backend API
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Check frontend
open http://localhost:3000
# Should show login page
```

### 8. Access the System

You now have three terminals running:
1. Temporal Server (`temporal server start-dev`)
2. Backend (`uvicorn src.main:app --reload`)
3. Frontend (`npm start`)

Access points:
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8080

**Default Login** (development only):
- Email: `admin@example.com`
- Password: `admin123`

## Testing the System

### Create Test Workflow

The system needs running Temporal workflows to display release data. Create a test workflow:

```python
# test_workflow.py
from temporalio import workflow, activity
from temporalio.client import Client
import asyncio

@workflow.defn
class ReleaseWorkflow:
    def __init__(self):
        self.state = "pending"
        self.wave_ids = []

    @workflow.run
    async def run(self, release_id: str) -> str:
        self.state = "in_progress"
        self.wave_ids = ["wave:wave-1"]
        await asyncio.sleep(3600)  # Run for 1 hour
        self.state = "completed"
        return release_id

    @workflow.query
    def get_release_state(self) -> dict:
        return {
            "id": workflow.info().workflow_id,
            "state": self.state,
            "workflow_id": workflow.info().workflow_id,
            "wave_ids": self.wave_ids
        }

async def main():
    client = await Client.connect("localhost:7233")

    # Start test workflow
    handle = await client.start_workflow(
        ReleaseWorkflow.run,
        "release:test-001",
        id="release:test-001",
        task_queue="releases"
    )
    print(f"Started workflow: {handle.id}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python test_workflow.py
```

### Verify in Frontend

1. Open http://localhost:3000
2. Login with default credentials
3. You should see `release:test-001` in the release list
4. Click it to view details

## Development Workflow

### Running the Full Stack

You need 3 terminals:

**Terminal 1 - Temporal**:
```bash
temporal server start-dev
```

**Terminal 2 - Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend**:
```bash
cd frontend
npm start
```

All three support hot reload - code changes will automatically restart the services.

### Run Tests

**Backend**:
```bash
cd backend
pytest
```

**Frontend**:
```bash
cd frontend
npm test
```

**E2E**:
```bash
cd frontend
npx playwright test
```

## Architecture Overview

```
┌─────────────┐
│   Browser   │
│  (React +   │
│  Chakra UI) │
│  Port 3000  │
└──────┬──────┘
       │ HTTP/REST
       ↓
┌──────────────┐
│   FastAPI    │
│   Backend    │
│     (BFF)    │
│  Port 8000   │
└──────┬───────┘
       │ Query
       ↓
┌──────────────┐
│   Temporal   │
│   Server     │
│ (Local Dev)  │
│  Port 7233   │
│  UI: 8080    │
└──────────────┘
```

## Key Concepts

### Entity Hierarchy

```
Release (N)
  └── Wave (N per release)
        └── Cluster (N per wave)
              └── Bundle (1 per cluster)
                    └── App (N per bundle)
```

**Important**: Each cluster contains exactly 1 bundle.

### Entity ID Format

All entities use the format: `{type}:{id}`

Examples:
- `release:rel-2025-01`
- `wave:wave-1`
- `cluster:us-west`
- `bundle:web-services`
- `app:api-gateway`

### State Flow

1. **Temporal Workflow** maintains entity state
2. **Backend BFF** queries workflow via Temporal SDK
3. **Frontend** fetches from Backend REST API
4. **User** views state in dashboard

## Common Tasks

### Add a New User

```bash
# Use backend CLI (to be implemented)
python backend/cli.py create-user \
  --email newuser@example.com \
  --password password123 \
  --full-name "New User"
```

### Query Release via API

```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@example.com&password=admin123" \
  | jq -r '.access_token')

# List releases
curl http://localhost:8000/api/releases \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Get release hierarchy
curl http://localhost:8000/api/releases/release:test-001/hierarchy \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### View Temporal Workflows

Open Temporal UI: http://localhost:8080

- See all running workflows
- Query workflow state manually
- View workflow history

### Check Logs

Logs appear in the respective terminals:
- **Temporal logs**: Terminal 1 (where `temporal server start-dev` is running)
- **Backend logs**: Terminal 2 (uvicorn output)
- **Frontend logs**: Terminal 3 (npm start output)

## Troubleshooting

### Backend won't start

**Symptom**: Backend fails to start or crashes

**Solutions**:
1. Check Temporal is running: Open http://localhost:8080
2. Verify environment variables in `.env` (especially `TEMPORAL_HOST=localhost:7233`)
3. Check port 8000 is not already in use: `lsof -i :8000`
4. Ensure virtual environment is activated: `source venv/bin/activate`
5. Check Python version: `python --version` (should be 3.11+)

### Frontend won't connect to backend

**Symptom**: API errors in browser console

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS configuration in backend `.env`
3. Verify `REACT_APP_API_URL` in frontend environment

### No releases showing in list

**Symptom**: Empty release list in frontend

**Solutions**:
1. Check if any workflows are running in Temporal UI
2. Verify workflows have correct query handlers
3. Check backend logs for Temporal connection errors

### Authentication fails

**Symptom**: Login returns 401

**Solutions**:
1. Verify default user exists (check backend startup logs in Terminal 2)
2. Check JWT_SECRET is set in backend `.env`
3. Restart backend if needed (Ctrl+C in Terminal 2, then rerun uvicorn command)

## Next Steps

1. **Read the Spec**: See [spec.md](./spec.md) for detailed requirements
2. **Explore API**: Visit http://localhost:8000/docs for interactive API documentation
3. **View Architecture**: See [plan.md](./plan.md) for technical architecture
4. **Understand Data Model**: See [data-model.md](./data-model.md) for entity definitions
5. **Run Tests**: Execute test suite to verify everything works
6. **Create Tasks**: Run `/speckit.tasks` to generate implementation tasks

## Production Deployment

For production deployment:

1. **Change secrets**: Generate secure JWT_SECRET
2. **Configure Temporal**: Point to production Temporal cluster
3. **Enable HTTPS**: Use reverse proxy (nginx, Traefik)
4. **Set CORS**: Limit CORS origins to production domain
5. **Configure logging**: Use structured logging with log aggregation
6. **Set resource limits**: Configure Docker resource constraints
7. **Enable monitoring**: Add Prometheus/Grafana for metrics
8. **Backup strategy**: Plan for data persistence

See deployment documentation for detailed production setup.

## Resources

- **Temporal Docs**: https://docs.temporal.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Chakra UI Docs**: https://chakra-ui.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/

## Support

For issues or questions:
1. Check Temporal UI for workflow status
2. Review backend logs for errors
3. Check frontend console for errors
4. Consult spec and architecture docs
5. File an issue if problem persists
