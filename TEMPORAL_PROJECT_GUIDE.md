 # 🎓 Temporal Release Management System - Complete Guide

**Author:** Claude
**Date:** November 2025
**Project:** BFF-Temporal Release Management System

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [What is Temporal?](#2-what-is-temporal)
3. [Python Syntax Primer](#3-python-syntax-primer)
4. [System Architecture](#4-system-architecture)
5. [How Temporal Workflows Work](#5-how-temporal-workflows-work)
6. [The Worker](#6-the-worker)
7. [Starting a Workflow](#7-starting-a-workflow)
8. [Querying Workflows](#8-querying-workflows)
9. [The Backend API](#9-the-backend-api)
10. [Key Python Patterns](#10-key-python-patterns)
11. [Complete Request Flow](#11-complete-request-flow)
12. [Why Use Temporal?](#12-why-use-temporal)
13. [Common Patterns & Best Practices](#13-common-patterns--best-practices)
14. [Project File Structure](#14-project-file-structure)
15. [Debugging Tips](#15-debugging-tips)
16. [Summary](#16-summary)

---

## 1. PROJECT OVERVIEW

### What Are We Building?

This is a **Release Management System** that tracks software deployments using **Temporal workflows**. Think of it like tracking a package delivery, but for deploying software to servers.

### The 5-Level Hierarchy

```
Release (e.g., "Deploy version 2.0")
  └─ Wave 1 (Deploy to 25% of servers)
      └─ Cluster 1-1 (US-East servers)
          └─ Bundle (Group of apps)
              └─ App 1 (Payment Service)
              └─ App 2 (User Service)
      └─ Cluster 1-2 (US-West servers)
          └─ Bundle...
  └─ Wave 2 (Deploy to next 25%)
      └─ Clusters...
```

**Use Case:**
Deploy a new version of your software gradually across thousands of servers. If something goes wrong, you can pause, rollback, or fix issues before continuing.

---

## 2. WHAT IS TEMPORAL?

**Temporal** is a platform for writing **long-running, reliable workflows**. Think of it as a "super-durable async/await."

### Traditional Problem

```python
# Normal code - if server crashes, you lose everything!
def deploy_release():
    deploy_wave_1()  # Takes 2 hours
    deploy_wave_2()  # Takes 2 hours
    # If server crashes here, you lose all progress!
```

### Temporal Solution

Temporal **saves your progress** after each step. If the server crashes, it resumes exactly where it left off!

### Key Concepts

1. **Workflow** = A durable function that can run for days/months
2. **Worker** = A server that executes workflow code
3. **Task Queue** = A message queue where workflows wait for workers
4. **Query** = Ask a running workflow for its current state
5. **Activity** = External side-effect (API calls, database writes)

### How It Works

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Client     │         │   Temporal   │         │    Worker    │
│              │         │    Server    │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                        │
       │ Start Workflow         │                        │
       │───────────────────────>│                        │
       │                        │                        │
       │                        │ Schedule Task          │
       │                        │───────────────────────>│
       │                        │                        │
       │                        │                        │ Execute
       │                        │                        │ Workflow
       │                        │                        │ Code
       │                        │                        │
       │                        │<───────────────────────│
       │                        │  Report Progress       │
       │                        │  (State Saved!)        │
       │                        │                        │
       │ Query Workflow State   │                        │
       │───────────────────────>│                        │
       │<───────────────────────│                        │
       │  Return State          │                        │
```

### Benefits

- ✅ **Fault Tolerant** - Survives crashes, restarts automatically
- ✅ **Long Running** - Can run for days, weeks, or months
- ✅ **Observable** - Query state anytime while running
- ✅ **Scalable** - Add more workers to handle more workflows
- ✅ **Time Travel** - Debug by replaying workflow history
- ✅ **Reliable** - Guaranteed execution of workflows

---

## 3. PYTHON SYNTAX PRIMER

### A. Type Hints (Python 3.10+)

```python
# Type hints tell Python (and you) what type each variable is

def greet(name: str) -> str:
    #        ^^^^        ^^^^
    #        |           |
    #        parameter   return type
    #        type
    return f"Hello, {name}"

# Variables
age: int = 25
names: list[str] = ["Alice", "Bob"]
user: dict[str, int] = {"age": 25}
```

**Why Use Type Hints?**
- Better IDE autocomplete
- Catch bugs before runtime
- Self-documenting code
- Required by some tools (FastAPI)

### B. Async/Await (Asynchronous Programming)

```python
# Synchronous (blocking) - waits for each task to finish
def make_coffee():
    boil_water()      # Wait 5 minutes
    brew_coffee()     # Wait 3 minutes
    # Total: 8 minutes

# Asynchronous (non-blocking) - can do multiple things at once
async def make_coffee():
    await boil_water()   # Start boiling (can do other things while waiting)
    await brew_coffee()  # Start brewing (can overlap!)
    # Can be faster if tasks can run in parallel

# To run async functions:
import asyncio
asyncio.run(make_coffee())
```

**When to Use Async:**
- I/O operations (network requests, database queries)
- Multiple concurrent operations
- Long-running tasks that wait for external events

### C. Decorators

```python
# A decorator modifies or wraps a function

@workflow.defn  # ← This is a decorator
class MyWorkflow:
    pass

# It's the same as:
class MyWorkflow:
    pass
MyWorkflow = workflow.defn(MyWorkflow)

# Common decorators in this project:
@workflow.defn       # Marks a class as a workflow
@workflow.run        # Marks the main workflow method
@workflow.query      # Marks a query handler
@app.get("/path")    # Marks an HTTP GET endpoint (FastAPI)
```

### D. F-Strings (Formatted Strings)

```python
name = "Alice"
age = 25

# F-strings let you embed variables in strings
message = f"Hello, {name}! You are {age} years old."
# Result: "Hello, Alice! You are 25 years old."

# Can include expressions:
wave_id = f"wave:wave-{i+1}"  # If i=0, result: "wave:wave-1"

# Can format numbers:
pi = 3.14159
print(f"Pi is approximately {pi:.2f}")  # "Pi is approximately 3.14"
```

### E. List Comprehensions

```python
# Traditional way:
numbers = []
for i in range(5):
    numbers.append(i * 2)
# Result: [0, 2, 4, 6, 8]

# List comprehension (one line):
numbers = [i * 2 for i in range(5)]
# Same result: [0, 2, 4, 6, 8]

# With condition:
even_numbers = [i for i in range(10) if i % 2 == 0]
# Result: [0, 2, 4, 6, 8]

# In the project:
self.wave_ids = [f"wave:wave-{i+1}" for i in range(num_waves)]
# If num_waves=3: ["wave:wave-1", "wave:wave-2", "wave:wave-3"]
```

### F. Classes and `__init__`

```python
class Person:
    def __init__(self, name: str, age: int):
        # __init__ is the constructor - runs when you create an instance
        self.name = name  # self = "this instance"
        self.age = age

    def greet(self):
        print(f"Hello, I'm {self.name}")

# Create an instance:
person = Person("Alice", 25)
print(person.name)  # "Alice"
person.greet()      # "Hello, I'm Alice"
```

---

## 4. SYSTEM ARCHITECTURE

### Component Diagram

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Frontend   │ ───────>│   Backend   │ ───────>│  Temporal   │
│  (React)    │  HTTP   │  (FastAPI)  │  gRPC   │   Server    │
│             │<────── │             │<─────── │             │
└─────────────┘         └─────────────┘         └─────────────┘
                               │                       ▲
                               │                       │
                               ▼                       │
                        ┌─────────────┐               │
                        │   Worker    │ ──────────────┘
                        │  (Python)   │  Executes workflows
                        └─────────────┘
```

### Components

1. **Frontend (React + TypeScript)**
   - Port: 3000
   - Shows dashboard with releases
   - Makes HTTP requests to backend
   - Uses Chakra UI for styling

2. **Backend (FastAPI + Python)**
   - Port: 8000
   - REST API endpoints
   - Queries Temporal for workflow state
   - Handles authentication (JWT)

3. **Temporal Server**
   - Port: 7233 (gRPC), 8080 (Web UI)
   - Stores workflow state
   - Manages task queues
   - Handles workflow scheduling

4. **Worker (Python)**
   - Executes workflow code
   - Polls Temporal for tasks
   - Can have multiple workers for scale

### Data Flow

```
User Action (Frontend)
    ↓
HTTP Request to Backend
    ↓
Backend queries Temporal
    ↓
Temporal returns workflow state
    ↓
Backend formats response
    ↓
Frontend displays data
```

---

## 5. HOW TEMPORAL WORKFLOWS WORK

### Complete Workflow Example

```python
@workflow.defn  # ← Decorator: "This class is a Temporal workflow"
class ReleaseWorkflow:
    """A workflow is like a durable async function."""

    def __init__(self) -> None:
        """
        Constructor - initializes the workflow's state.

        IMPORTANT: This state is saved by Temporal!
        If the worker crashes, Temporal recreates the workflow
        with this exact state preserved.
        """
        self.release_id: str = ""
        self.state: str = "pending"
        self.wave_ids: list[str] = []
        # These variables survive crashes!

    @workflow.run  # ← Decorator: "This is the main workflow method"
    async def run(self, release_id: str, num_waves: int = 2) -> str:
        """
        The workflow's main logic.

        Args:
            release_id: Identifier like "release:rel-2025-01"
            num_waves: Number of deployment waves (default 2)

        Returns:
            The release_id when complete
        """
        # Step 1: Initialize state
        self.release_id = release_id
        self.workflow_id = workflow.info().workflow_id
        self.created_at = workflow.now().isoformat()

        # Step 2: Generate child entity IDs
        # List comprehension: creates ["wave:wave-1", "wave:wave-2"]
        self.wave_ids = [f"wave:wave-{i+1}" for i in range(num_waves)]

        # Step 3: Change state to in_progress
        self.state = "in_progress"
        self.updated_at = workflow.now().isoformat()

        # Step 4: Sleep for 1 hour (workflow stays alive)
        # CRITICAL: Use workflow.sleep(), NOT Python's time.sleep()!
        # workflow.sleep() tells Temporal "pause this workflow"
        await workflow.sleep(3600)  # 3600 seconds = 1 hour

        # Step 5: Mark as completed
        self.state = "completed"
        self.updated_at = workflow.now().isoformat()

        return release_id

    @workflow.query  # ← Decorator: "This is a query handler"
    def get_release_state(self) -> dict:
        """
        Query handler - returns current state WITHOUT modifying it.

        The frontend can call this to see the workflow's current state
        while it's running.

        Returns:
            Dictionary with current workflow state
        """
        return {
            "id": self.release_id,
            "state": self.state,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "wave_ids": self.wave_ids,
        }
```

### Key Temporal Concepts

#### 1. Workflow Determinism

Workflows must be **deterministic** - they must produce the same result when replayed.

```python
# ❌ DON'T DO THIS - non-deterministic (changes each time)
import time
import random

timestamp = time.time()  # Different each replay!
value = random.random()  # Different each replay!

# ✅ DO THIS - deterministic (same each replay)
timestamp = workflow.now()  # Temporal controls this
value = workflow.random()   # Temporal controls this
```

**Why?** Temporal replays workflows to recover from crashes. If code is non-deterministic, replay might produce different results.

#### 2. Durable Sleep

```python
# ❌ DON'T DO THIS
import time
time.sleep(3600)  # Blocks the worker thread for 1 hour!

# ✅ DO THIS
await workflow.sleep(3600)  # Temporal manages this, worker is free
```

**Benefits:**
- Worker thread is freed immediately
- Other workflows can execute
- Survives worker restarts

#### 3. Workflow State Persistence

```python
# Every time you modify self.something, Temporal saves it:
self.state = "in_progress"  # ← Temporal saves this!

# If worker crashes and restarts:
# 1. Temporal replays the workflow from the beginning
# 2. self.state is restored to "in_progress"
# 3. Workflow continues from where it left off
```

### Workflow Lifecycle

```
1. Start Workflow
   ↓
2. Execute run() method
   ↓
3. State changes are saved
   ↓
4. await workflow.sleep() - workflow pauses
   ↓
5. Worker can shutdown (workflow survives!)
   ↓
6. Time elapses...
   ↓
7. Worker wakes up and resumes
   ↓
8. Continue execution
   ↓
9. Workflow completes
```

---

## 6. THE WORKER

### What is a Worker?

A **Worker** is a process that:
- Connects to Temporal Server
- Polls a task queue for work
- Executes workflow and activity code
- Reports results back to Temporal

### Worker Code

```python
async def main() -> None:
    # Step 1: Connect to Temporal Server
    client = await Client.connect("localhost:7233")

    # Step 2: Create a worker
    worker = Worker(
        client,
        task_queue="release-task-queue",  # ← Listen on this queue
        workflows=[
            ReleaseWorkflow,  # ← Register workflows the worker can execute
            WaveWorkflow,
            ClusterWorkflow,
            BundleWorkflow,
            AppWorkflow,
        ],
    )

    # Step 3: Start the worker (runs forever)
    await worker.run()  # ← Blocks here, waiting for workflows

# Run it
if __name__ == "__main__":
    asyncio.run(main())
```

### What the Worker Does

1. **Connects** to Temporal Server
2. **Polls** the task queue for workflow tasks
3. **Executes** workflow code when task arrives
4. **Reports** results back to Temporal
5. **Repeats** - goes back to polling

### Multiple Workers

You can run multiple workers for:
- **High availability** - If one crashes, others continue
- **Scalability** - Handle more concurrent workflows
- **Load balancing** - Temporal distributes work

```bash
# Terminal 1
python worker.py

# Terminal 2
python worker.py

# Both workers share the work!
```

### Worker Crash Recovery

```
Worker 1 executing workflow:
├─ Step 1: Initialize (SAVED ✓)
├─ Step 2: Deploy wave 1 (SAVED ✓)
├─ Worker 1 CRASHES 💥
│
Worker 2 picks up workflow:
├─ Step 3: Deploy wave 2 (resumes here!)
└─ Step 4: Complete
```

---

## 7. STARTING A WORKFLOW

### Client Code

```python
async def create_test_release(client: Client, release_id: str, num_waves: int = 2):
    """Start a workflow execution."""

    # Start the workflow
    release_handle = await client.start_workflow(
        ReleaseWorkflow.run,              # ← Which workflow method to run
        args=[release_id, num_waves],     # ← Arguments to pass
        id=release_id,                    # ← Unique workflow ID
        task_queue="release-task-queue",  # ← Which queue to use
    )

    # The workflow is now running!
    # You can:
    # - Query it: await release_handle.query("get_release_state")
    # - Cancel it: await release_handle.cancel()
    # - Wait for result: result = await release_handle.result()
```

### Execution Flow

```
1. Client sends "start workflow" command to Temporal Server
   ↓
2. Temporal Server:
   - Creates workflow record
   - Assigns unique ID
   - Puts task on "release-task-queue"
   ↓
3. Worker polling the queue picks up the task
   ↓
4. Worker creates ReleaseWorkflow instance
   ↓
5. Worker executes ReleaseWorkflow.run(release_id, num_waves)
   ↓
6. Workflow runs until:
   - Completes
   - Awaits (e.g., workflow.sleep())
   - Errors
   ↓
7. Temporal saves state after each step
```

### Workflow ID Rules

- Must be **unique** per workflow
- Can reuse ID after workflow completes
- If you start workflow with existing ID: **error** (unless workflow completed)

```python
# First call - OK
await client.start_workflow(ReleaseWorkflow.run, id="release:rel-1", ...)

# Second call with same ID - ERROR!
await client.start_workflow(ReleaseWorkflow.run, id="release:rel-1", ...)
# Raises: WorkflowAlreadyStartedError
```

---

## 8. QUERYING WORKFLOWS

### What is a Query?

A **query** reads workflow state **without modifying it**.

```python
@workflow.query
def get_release_state(self) -> dict:
    """Query handler - returns current state."""
    return {
        "id": self.release_id,
        "state": self.state,
        # ... return read-only data
    }
```

### Querying from Client

```python
# Get handle to running workflow
handle = client.get_workflow_handle(workflow_id="release:rel-2025-01")

# Execute query
result = await handle.query("get_release_state")

# result = {
#     "id": "release:rel-2025-01",
#     "state": "in_progress",
#     "created_at": "2025-11-07T10:00:00+00:00",
#     ...
# }
```

### Backend Query Service

```python
# In backend/src/services/temporal_client.py

async def query_workflow(self, workflow_id: str, query_name: str):
    """Query a running workflow."""

    # Get a handle to the workflow
    handle = self._client.get_workflow_handle(workflow_id)

    # Execute the query (calls the @workflow.query method)
    result = await handle.query(query_name)

    return result

# Usage:
result = await client.query_workflow(
    workflow_id="release:rel-2025-01",
    query_name="get_release_state"
)
```

### Query vs Signal

| Feature        | Query              | Signal |
|---------       | -------            |--------|
| Purpose        | Read state         | Modify state |
| Changes state? | No                 | Yes |
| Returns value? | Yes                | No |
| Example        | Get current status | Pause workflow |

---

## 9. THE BACKEND API

### FastAPI Endpoint

```python
# backend/src/api/releases.py

@router.get("/releases", response_model=PaginatedReleases)
async def list_releases(
    current_user: Annotated[User, Depends(get_current_user)],
    entity_service: Annotated[EntityService, Depends(get_entity_service)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedReleases:
    """
    HTTP GET /api/releases endpoint.

    Args:
        current_user: Injected by FastAPI (from JWT token)
        entity_service: Injected by FastAPI (dependency injection)
        page: Query parameter (?page=1)
        page_size: Query parameter (?page_size=20)

    Returns:
        JSON with list of releases
    """
    # Call the entity service to get releases
    result = await entity_service.list_releases(page=page, page_size=page_size)

    return PaginatedReleases(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )
```

### Request Flow

```
1. Frontend makes HTTP GET request:
   GET http://localhost:8000/api/releases?page=1&page_size=20
   Header: Authorization: Bearer <jwt_token>

2. FastAPI middleware processes request:
   - CORS middleware
   - Security headers
   - Rate limiting

3. FastAPI routes to list_releases()

4. FastAPI resolves dependencies:
   - get_current_user() validates JWT token
   - get_entity_service() creates service instance

5. list_releases() executes:
   a. Calls entity_service.list_releases()
   b. Service queries Temporal for workflows
   c. Returns formatted results

6. FastAPI serializes response to JSON

7. Response sent to frontend
```

### Entity Service

```python
# backend/src/services/entity_service.py

async def list_releases(self, page: int = 1, page_size: int = 20):
    """List all releases with pagination."""

    # Step 1: List all workflow IDs from Temporal
    all_workflow_ids = await self.temporal_client.list_workflows(
        query="",  # Empty query returns all workflows
        max_results=1000,
    )

    # Step 2: Filter for release workflows
    release_ids = [wf_id for wf_id in all_workflow_ids
                   if wf_id.startswith("release:")]

    # Step 3: Calculate pagination
    total = len(release_ids)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_ids = release_ids[start_idx:end_idx]

    # Step 4: Query each release for its state
    releases = []
    for release_id in paginated_ids:
        try:
            release = await self.get_release(release_id)
            releases.append(release)
        except Exception as e:
            logger.error(f"Error getting release {release_id}: {e}")

    return {
        "items": releases,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
```

---

## 10. KEY PYTHON PATTERNS

### Pattern 1: Dependency Injection (FastAPI)

```python
# FastAPI automatically "injects" dependencies

async def list_releases(
    current_user: Annotated[User, Depends(get_current_user)],
    #                               ^^^^^^^^^^^^^^^^^^^^^^
    #                               FastAPI calls this function first
):
    # current_user is automatically populated!
    pass
```

### Pattern 2: Pydantic Models (Data Validation)

```python
from pydantic import BaseModel, Field

class Release(BaseModel):
    """Pydantic validates data automatically."""
    id: str = Field(..., pattern=r"^release:")  # Must start with "release:"
    state: str = Field(..., min_length=1, max_length=50)
    created_at: datetime

# If you try to create invalid data:
release = Release(id="invalid", state="", created_at="not a date")
# ❌ Raises ValidationError!

# Valid:
release = Release(
    id="release:rel-1",
    state="pending",
    created_at="2025-11-07T10:00:00Z"
)
# ✅ Works! Data is validated and converted to proper types
```

### Pattern 3: Context Managers (with statement)

```python
# Context manager ensures cleanup

async with self._connection_lock:
    # Lock is acquired
    await self.connect()
    # Lock is automatically released, even if exception occurs

# Equivalent to:
try:
    await self._connection_lock.acquire()
    await self.connect()
finally:
    self._connection_lock.release()
```

### Pattern 4: Middleware (FastAPI)

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Runs on EVERY request."""

    async def dispatch(self, request: Request, call_next):
        # Before handler
        print("Request received:", request.url)

        response = await call_next(request)  # Call the actual handler

        # After handler - add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
```

### Pattern 5: Singleton Pattern

```python
# Global instance (created once)
_temporal_client: Optional[TemporalClientWrapper] = None

async def get_temporal_client() -> TemporalClientWrapper:
    """Get or create global Temporal client instance."""
    global _temporal_client
    if _temporal_client is None:
        _temporal_client = TemporalClientWrapper()
        await _temporal_client.connect()
    return _temporal_client
    # Returns same instance for all calls
```

---

## 11. COMPLETE REQUEST FLOW

### User Clicks "View Releases"

```
USER CLICKS "View Releases" ON FRONTEND
   ↓
1. Frontend (React):
   axios.get('http://localhost:8000/api/releases', {
     headers: { Authorization: 'Bearer <token>' }
   })
   ↓
2. Backend API (FastAPI):
   Middleware chain:
   - SecurityHeadersMiddleware (adds security headers)
   - RateLimitMiddleware (checks rate limits)
   - CORSMiddleware (validates origin)
   ↓
3. Router matches endpoint:
   @router.get("/releases")
   async def list_releases(...)
   ↓
4. Dependency Resolution:
   a. Depends(get_current_user):
      - Extract JWT token from header
      - Verify token signature
      - Decode token payload
      - Look up user in database
      - Return User object

   b. Depends(get_entity_service):
      - Get/create Temporal client
      - Create EntityService instance
      - Return EntityService
   ↓
5. Execute Endpoint:
   result = await entity_service.list_releases(page=1, page_size=20)
   ↓
6. Entity Service:
   a. List all workflow IDs from Temporal
      workflows = await temporal_client.list_workflows("")
      # Returns: ["release:rel-1", "wave:wave-1", "cluster:...", ...]

   b. Filter for releases
      release_ids = [id for id in workflows if id.startswith("release:")]
      # Returns: ["release:rel-1", "release:rel-2"]

   c. Query each release workflow
      for release_id in release_ids:
          state = await temporal_client.query_workflow(
              workflow_id=release_id,
              query_name="get_release_state"
          )
          releases.append(Release(**state))
   ↓
7. Temporal Server:
   - Finds running workflow by ID
   - Calls workflow's get_release_state() query handler
   - Returns current state
   ↓
8. Backend formats response:
   {
     "items": [
       {
         "id": "release:rel-1",
         "state": "in_progress",
         "workflow_id": "release:rel-1",
         "created_at": "2025-11-07T10:00:00Z",
         "updated_at": "2025-11-07T10:30:00Z",
         "wave_ids": ["wave:wave-1", "wave:wave-2"]
       }
     ],
     "total": 1,
     "page": 1,
     "page_size": 20
   }
   ↓
9. Frontend receives JSON:
   - Parses response
   - Updates React state
   - Re-renders ReleaseList component
   ↓
10. User sees releases in table
```

---

## 12. WHY USE TEMPORAL?

### The Problem

**Scenario:** Deploy software to 1000 servers (takes 10 hours)

**Traditional Approach:**
```python
def deploy():
    for server in servers:
        deploy_to_server(server)  # Takes ~30 seconds each
```

**What Could Go Wrong?**
- ❌ Server crashes after 500 deployments → **Start over from beginning!**
- ❌ Need to pause deployment? → **Can't!**
- ❌ Want to see progress? → **Add complex logging and state management**
- ❌ Deployment fails on server 789? → **Hard to retry just that one**
- ❌ Need to rollback? → **Write custom rollback logic**

### With Temporal

```python
@workflow.defn
class DeployWorkflow:
    def __init__(self):
        self.deployed_count = 0  # ← State saved by Temporal!
        self.failed_servers = []

    @workflow.run
    async def run(self, servers: list[str]):
        for server in servers:
            try:
                # Execute deployment as an activity
                await workflow.execute_activity(
                    deploy_to_server,
                    server,
                    start_to_close_timeout=timedelta(minutes=5)
                )
                self.deployed_count += 1  # ← Saved!
            except Exception as e:
                self.failed_servers.append(server)

            # If crash happens here, resumes from deployed_count!

        return f"Deployed to {self.deployed_count} servers"

    @workflow.query
    def get_progress(self):
        return {
            "deployed": self.deployed_count,
            "total": len(servers),
            "failed": self.failed_servers
        }
```

**Benefits:**
- ✅ **Automatic state persistence** - Never lose progress
- ✅ **Pause/resume anytime** - Signal workflow to pause
- ✅ **Query progress while running** - See real-time status
- ✅ **Retry logic built-in** - Configurable retry policies
- ✅ **Survives crashes** - Pick up exactly where it left off
- ✅ **Observability** - Full history in Temporal UI
- ✅ **Rollback** - Implement compensating actions

### Real-World Use Cases

1. **E-commerce Order Processing**
   - Charge payment
   - Update inventory
   - Send confirmation email
   - Ship order
   - Track delivery
   - (Can take days, needs to be reliable)

2. **CI/CD Pipeline**
   - Run tests
   - Build artifacts
   - Deploy to staging
   - Wait for approval
   - Deploy to production
   - Monitor health

3. **Data Processing**
   - Ingest data (hours)
   - Transform data (hours)
   - Load to warehouse (hours)
   - Generate reports
   - Send notifications

4. **User Onboarding**
   - Send welcome email
   - Wait 1 day
   - Send tutorial email
   - Wait 3 days
   - Send feature highlights
   - Wait 7 days
   - Ask for feedback

---

## 13. COMMON PATTERNS & BEST PRACTICES

### Pattern 1: List Comprehensions

```python
# Instead of:
wave_ids = []
for i in range(num_waves):
    wave_ids.append(f"wave:wave-{i+1}")

# Use:
wave_ids = [f"wave:wave-{i+1}" for i in range(num_waves)]

# Benefits:
# - More concise
# - More readable
# - Often faster
```

### Pattern 2: Async/Await for I/O

```python
# ❌ Synchronous (blocks entire thread)
def get_user_data(user_id):
    profile = database.get_profile(user_id)      # Wait...
    orders = database.get_orders(user_id)        # Wait...
    preferences = database.get_preferences(user_id)  # Wait...
    return profile, orders, preferences
# Total time: 3 seconds (sequential)

# ✅ Asynchronous (non-blocking)
async def get_user_data(user_id):
    # Run all three queries concurrently!
    profile, orders, preferences = await asyncio.gather(
        database.get_profile(user_id),
        database.get_orders(user_id),
        database.get_preferences(user_id)
    )
    return profile, orders, preferences
# Total time: 1 second (parallel)
```

### Pattern 3: Type Hints for Clarity

```python
# ❌ Without type hints - unclear what types are expected
def process(data):
    return data * 2

# ✅ With type hints - crystal clear
def process(data: int) -> int:
    return data * 2

# Benefits:
# - IDE autocomplete works better
# - Catch bugs early (type checkers)
# - Self-documenting code
# - FastAPI uses this for validation
```

### Pattern 4: Error Handling with Custom Exceptions

```python
# Define custom exceptions
class EntityNotFoundError(Exception):
    """Raised when entity is not found."""
    pass

# Use in code
async def get_release(release_id: str) -> Release:
    try:
        result = await temporal_client.query_workflow(
            workflow_id=release_id,
            query_name="get_release_state",
        )
        return Release(**result)
    except WorkflowNotFoundError:
        raise EntityNotFoundError(f"Release not found: {release_id}")

# Handle in API
@router.get("/releases/{release_id}")
async def get_release(release_id: str):
    try:
        return await service.get_release(release_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Release not found")
```

### Pattern 5: Dependency Injection

```python
# ❌ Without DI - hard to test
@app.get("/users")
async def list_users():
    db = Database.connect()  # Creates new connection every time
    users = await db.query("SELECT * FROM users")
    return users

# ✅ With DI - easy to test
async def get_database():
    return database_instance  # Reuses connection

@app.get("/users")
async def list_users(db: Annotated[Database, Depends(get_database)]):
    users = await db.query("SELECT * FROM users")
    return users

# Testing:
app.dependency_overrides[get_database] = lambda: MockDatabase()
```

### Best Practices

1. **Use async/await for I/O operations**
   - Network requests
   - Database queries
   - File operations

2. **Use type hints everywhere**
   - Function parameters
   - Return types
   - Class attributes

3. **Handle errors explicitly**
   - Don't use bare `except:`
   - Use custom exceptions
   - Log errors properly

4. **Use f-strings for formatting**
   - More readable than `.format()`
   - More efficient than `%` formatting

5. **Use list comprehensions**
   - When creating lists from iterables
   - Keep them simple (not nested)

6. **Use Pydantic for validation**
   - Validate API inputs
   - Validate configuration
   - Serialize/deserialize data

---

## 14. PROJECT FILE STRUCTURE

```
bff-temporal/
│
├── backend/
│   ├── src/
│   │   ├── main.py                    # FastAPI app entry point
│   │   │
│   │   ├── api/                       # HTTP endpoint handlers
│   │   │   ├── __init__.py
│   │   │   ├── releases.py            # /api/releases endpoints
│   │   │   ├── entities.py            # /api/waves, /api/clusters, etc.
│   │   │   └── auth.py                # /api/auth/login endpoint
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── temporal_client.py     # Temporal connection wrapper
│   │   │   ├── entity_service.py      # Query workflows for entities
│   │   │   └── auth_service.py        # User authentication
│   │   │
│   │   ├── models/                    # Pydantic data models
│   │   │   ├── __init__.py
│   │   │   ├── entities.py            # Release, Wave, Cluster, etc.
│   │   │   └── auth.py                # User, Token models
│   │   │
│   │   ├── middleware/                # Request/response interceptors
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # Security headers
│   │   │   └── rate_limit.py          # Rate limiting
│   │   │
│   │   └── core/                      # Core utilities
│   │       ├── __init__.py
│   │       ├── config.py              # Settings management
│   │       ├── logging.py             # Logging configuration
│   │       ├── security.py            # JWT functions
│   │       └── validation.py          # Common validators
│   │
│   ├── tests/                         # Tests
│   │   ├── unit/                      # Unit tests
│   │   ├── integration/               # Integration tests
│   │   └── contract/                  # Contract tests
│   │
│   ├── test_workflows.py              # Workflow definitions
│   ├── worker.py                      # Temporal worker
│   ├── .env                           # Environment variables
│   ├── .env.example                   # Example environment file
│   ├── requirements.txt               # Python dependencies
│   └── pyproject.toml                 # Project configuration
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                    # Main React component
│   │   │
│   │   ├── components/                # UI components
│   │   │   ├── Layout.tsx             # Page layout wrapper
│   │   │   ├── ReleaseList.tsx        # Displays releases table
│   │   │   ├── EntityTree.tsx         # Hierarchical tree view
│   │   │   ├── Login.tsx              # Login form
│   │   │   ├── ProtectedRoute.tsx     # Auth wrapper
│   │   │   └── ErrorBoundary.tsx      # Error handling
│   │   │
│   │   ├── pages/                     # Page components
│   │   │   ├── Dashboard.tsx          # Main dashboard
│   │   │   ├── LoginPage.tsx          # Login page
│   │   │   └── ReleaseDetailPage.tsx  # Release details
│   │   │
│   │   ├── services/                  # API clients
│   │   │   ├── api.ts                 # Axios configuration
│   │   │   ├── releaseService.ts      # Release API calls
│   │   │   └── authService.ts         # Auth API calls
│   │   │
│   │   ├── hooks/                     # React hooks
│   │   │   ├── useAuth.ts             # Authentication hook
│   │   │   └── useReleases.ts         # Releases data hook
│   │   │
│   │   ├── types/                     # TypeScript types
│   │   │   ├── entities.ts            # Entity type definitions
│   │   │   └── auth.ts                # Auth type definitions
│   │   │
│   │   └── index.tsx                  # App entry point
│   │
│   ├── public/                        # Static files
│   ├── .env                           # Environment variables
│   ├── package.json                   # Node dependencies
│   └── tsconfig.json                  # TypeScript config
│
├── specs/                             # Feature specifications
├── start-system.sh                    # Quick start script
└── README.md                          # Project documentation
```

### Key Files Explained

**Backend:**
- `main.py` - Creates FastAPI app, configures middleware, includes routers
- `worker.py` - Connects to Temporal, registers workflows, polls for tasks
- `test_workflows.py` - Defines all workflow classes (Release, Wave, etc.)
- `temporal_client.py` - Wraps Temporal client, handles connections/queries
- `entity_service.py` - Business logic for listing/querying entities
- `releases.py` - HTTP endpoint handlers for /api/releases
- `auth.py` - Authentication endpoints and dependencies

**Frontend:**
- `App.tsx` - Main component, sets up routing
- `ReleaseList.tsx` - Table component showing all releases
- `releaseService.ts` - Functions that call backend API
- `useReleases.ts` - React hook for fetching releases data
- `api.ts` - Axios client configuration (base URL, auth interceptor)

---

## 15. DEBUGGING TIPS

### Check Temporal Server

```bash
# View Temporal Web UI
open http://localhost:8080

# You should see:
# - List of workflows
# - Workflow execution history
# - Task queues
```

### Check Worker Status

```bash
# In worker terminal, you should see:
👂 Worker is now listening for workflow tasks...
   • Task Queue: release-task-queue
   • Workflows: Release, Wave, Cluster, Bundle, App

# If not running:
cd backend
source venv/bin/activate
python worker.py
```

### Check Backend API

```bash
# Health check
curl http://localhost:8000/health
# Should return:
# {"status":"healthy","temporal":"connected","api":"running"}

# API docs
open http://localhost:8000/docs

# Check logs in terminal running uvicorn
```

### Check Frontend

```bash
# In frontend terminal:
npm start
# Should see: Compiled successfully!

# Open browser console (F12)
# Check for errors
# Check Network tab for failed requests
```

### Debug Workflow State

```python
# Create debug script: debug_workflow.py
import asyncio
from temporalio.client import Client

async def debug_workflow(workflow_id: str):
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle(workflow_id)

    # Get current state
    state = await handle.query("get_release_state")
    print(f"Current state: {state}")

    # Get workflow info
    desc = await handle.describe()
    print(f"Status: {desc.status}")
    print(f"Start time: {desc.start_time}")

# Run:
asyncio.run(debug_workflow("release:rel-2025-01"))
```

### Common Issues

**1. "No releases found" but workflows are running**
- Check: Are workflows in correct namespace? (default)
- Check: Do workflow IDs start with "release:"?
- Check: Backend logs for errors

**2. "500 Internal Server Error"**
- Check: Backend terminal for stack trace
- Check: Temporal server is running
- Check: Worker is running
- Check: JWT token is valid

**3. "401 Unauthorized"**
- Check: JWT token in localStorage
- Check: Token not expired
- Check: Backend .env has correct JWT_SECRET

**4. Workflows show as "Failed"**
- Check: Worker logs for errors
- Check: Temporal UI → Workflow → History tab
- Check: Stack trace in Temporal UI

**5. "CORS error"**
- Check: Backend .env has correct API_CORS_ORIGINS
- Check: Frontend is on http://localhost:3000

### Useful Commands

```bash
# Check if Temporal is running
curl http://localhost:7233
# Should NOT return "Connection refused"

# List workflows using Temporal CLI
temporal workflow list --namespace default

# Describe specific workflow
temporal workflow describe --workflow-id release:rel-2025-01

# Query workflow
temporal workflow query \
  --workflow-id release:rel-2025-01 \
  --name get_release_state

# Restart backend with logs
cd backend
source venv/bin/activate
LOG_LEVEL=DEBUG uvicorn src.main:app --reload
```

---

## 16. SUMMARY

### What You've Learned

This project teaches you:

1. **Temporal Workflows**
   - Write durable, long-running workflows
   - Survive crashes and restarts
   - Query workflow state
   - Handle complex state management

2. **Python Async Programming**
   - async/await syntax
   - asyncio event loop
   - Concurrent operations
   - Non-blocking I/O

3. **FastAPI Web Framework**
   - REST API endpoints
   - Dependency injection
   - Request/response handling
   - Middleware
   - Authentication (JWT)

4. **React Frontend**
   - Component-based UI
   - State management
   - HTTP requests (axios)
   - TypeScript types

5. **System Design**
   - Multi-tier architecture
   - Client-server communication
   - Service layer pattern
   - Separation of concerns

6. **Python Best Practices**
   - Type hints
   - List comprehensions
   - Error handling
   - Code organization

### Key Takeaways

**Temporal = Reliable Distributed Systems Made Easy**

Write complex, long-running processes as if they were simple async functions:
- ✅ Automatic state persistence
- ✅ Fault tolerance built-in
- ✅ Observable and debuggable
- ✅ Scalable by design

**Python Async = Efficient I/O**

Use async/await for:
- Network requests
- Database queries
- Multiple concurrent operations
- Better resource utilization

**FastAPI = Modern Python Web Framework**

Features:
- Automatic API documentation
- Type-based validation
- Dependency injection
- High performance
- Easy to test

### Architecture Pattern

```
Frontend (React)
    ↓ HTTP
Backend API (FastAPI)
    ↓ gRPC
Temporal Server
    ↑ Poll for tasks
Worker (Python)
    ↑ Executes workflows
```

### The 5-Level Hierarchy

```
Release (Top-level deployment)
  └─ Wave (Phased rollout)
      └─ Cluster (Group of servers)
          └─ Bundle (Group of applications)
              └─ App (Individual application)
```

Each level is a separate workflow that can be queried independently.

### Critical Concepts

1. **Workflows are deterministic** - Must produce same result when replayed
2. **State is automatically saved** - Progress never lost
3. **Workers can crash safely** - Workflows continue on other workers
4. **Queries don't modify state** - Read-only operations
5. **Dependencies are injected** - Clean, testable code

### Next Steps

To deepen your understanding:

1. **Add new workflow types**
   - Create a rollback workflow
   - Add a pause/resume mechanism
   - Implement canary deployments

2. **Enhance the API**
   - Add filtering and sorting
   - Implement search
   - Add batch operations

3. **Improve observability**
   - Add metrics (Prometheus)
   - Add tracing (Jaeger)
   - Enhanced logging

4. **Add activities**
   - External API calls
   - Database operations
   - File operations

5. **Explore Temporal features**
   - Signals (modify workflow state)
   - Child workflows
   - Continue-as-new (infinite workflows)
   - Saga pattern (compensating transactions)

### Resources

**Temporal Documentation:**
- https://docs.temporal.io
- https://docs.temporal.io/develop/python

**FastAPI Documentation:**
- https://fastapi.tiangolo.com

**Python Async:**
- https://docs.python.org/3/library/asyncio.html

**React:**
- https://react.dev

---

## Appendix A: Common Temporal Patterns

### Pattern 1: Saga (Compensating Transactions)

```python
@workflow.defn
class OrderWorkflow:
    async def run(self, order_id: str):
        # Step 1: Reserve inventory
        await workflow.execute_activity(reserve_inventory, order_id)

        try:
            # Step 2: Charge payment
            await workflow.execute_activity(charge_payment, order_id)
        except Exception:
            # Compensate: Unreserve inventory
            await workflow.execute_activity(unreserve_inventory, order_id)
            raise

        try:
            # Step 3: Ship order
            await workflow.execute_activity(ship_order, order_id)
        except Exception:
            # Compensate: Refund payment and unreserve
            await workflow.execute_activity(refund_payment, order_id)
            await workflow.execute_activity(unreserve_inventory, order_id)
            raise
```

### Pattern 2: Human-in-the-Loop

```python
@workflow.defn
class ApprovalWorkflow:
    def __init__(self):
        self.approved = False

    @workflow.run
    async def run(self, request_id: str):
        # Send notification
        await workflow.execute_activity(send_approval_email, request_id)

        # Wait for approval (signal)
        await workflow.wait_condition(lambda: self.approved, timeout=timedelta(days=7))

        if not self.approved:
            return "Approval timed out"

        # Process approved request
        await workflow.execute_activity(process_request, request_id)
        return "Approved and processed"

    @workflow.signal
    def approve(self):
        """Called when user approves."""
        self.approved = True
```

### Pattern 3: Infinite Workflow (Continue-as-New)

```python
@workflow.defn
class MonitoringWorkflow:
    @workflow.run
    async def run(self, iteration: int = 0):
        # Check system health
        health = await workflow.execute_activity(check_health)

        if not health.ok:
            await workflow.execute_activity(send_alert, health)

        # Wait 1 minute
        await workflow.sleep(60)

        # Prevent history from growing too large
        if iteration > 1000:
            workflow.continue_as_new(iteration=0)
        else:
            workflow.continue_as_new(iteration=iteration + 1)
```

---

## Appendix B: Glossary

**Activity** - A function that performs side effects (API calls, database writes). Retriable and can fail.

**Async/Await** - Python syntax for asynchronous programming. `async def` defines async function, `await` calls it.

**Decorator** - Python syntax to modify functions/classes. Example: `@workflow.defn`

**Dependency Injection** - Pattern where dependencies are "injected" into functions rather than created inside them.

**FastAPI** - Modern Python web framework with automatic validation and documentation.

**F-String** - Python string formatting: `f"Hello, {name}"`

**List Comprehension** - Concise way to create lists: `[x*2 for x in range(5)]`

**Middleware** - Code that runs before/after every HTTP request.

**Pydantic** - Python library for data validation using type hints.

**Query** - Read workflow state without modifying it.

**Signal** - Modify workflow state from outside.

**Task Queue** - Queue where Temporal puts tasks for workers to execute.

**Temporal** - Platform for durable workflow execution.

**Type Hints** - Python syntax for specifying types: `name: str`

**Worker** - Process that executes workflow and activity code.

**Workflow** - Durable function that can run for long periods and survive failures.

---

**End of Guide**

*This guide covers the fundamentals of the Temporal Release Management System. Refer back to specific sections as you build and extend the project.*
