# Research: Temporal Release Management System

**Feature**: 001-temporal-bff-system
**Date**: 2025-11-06
**Purpose**: Document technical decisions, best practices, and implementation patterns

## Overview

This document captures research findings for building a BFF system that queries Temporal workflows to display release state. Key research areas: Temporal Python SDK query patterns, FastAPI + Temporal integration, real-time state updates, and React + Chakra UI patterns.

## 1. Temporal Workflow Query Patterns

### Decision
Use Temporal Python SDK's `query` feature to retrieve entity states from running workflows. Implement query handlers in workflows that return current state for each entity type.

### Rationale
- **Read-Only Access**: Queries don't modify workflow state, perfect for read-only BFF pattern
- **Consistency**: Queries return current workflow state directly - no sync lag or stale data
- **Performance**: Queries are synchronous and fast (<100ms typical)
- **Simplicity**: No separate database to maintain or synchronize

### Implementation Pattern
```python
# In Temporal workflow (example - not actual implementation)
@workflow.query
def get_release_state() -> ReleaseState:
    return self.current_state

# In BFF service
async def get_release(workflow_id: str) -> ReleaseState:
    handle = client.get_workflow_handle(workflow_id)
    return await handle.query("get_release_state")
```

### Alternatives Considered
1. **Database Snapshot**: Maintain a separate database synced from workflows
   - Rejected: Adds complexity, potential for stale data, violates YAGNI
2. **Event Sourcing**: Replay workflow history to build current state
   - Rejected: Slower than queries, unnecessary complexity for read-only access
3. **Workflow Signals**: Use signals to request state updates
   - Rejected: Signals modify workflow state; queries are more appropriate for read operations

### Best Practices from Temporal Documentation
- Keep query handlers fast (<1s) - no heavy computation
- Query handlers should be idempotent and side-effect free
- Use typed query names to avoid typos
- Handle workflow completion gracefully (queries fail on completed workflows)

## 2. FastAPI + Temporal Integration

### Decision
Use async FastAPI endpoints with Temporal Python SDK async client. Initialize Temporal client on application startup as a singleton.

### Rationale
- **Async Performance**: Both FastAPI and Temporal SDK support async/await for maximum throughput
- **Connection Pooling**: Single client instance reuses connections efficiently
- **Clean Separation**: API layer handles HTTP, service layer handles Temporal logic

### Implementation Pattern
```python
# Application startup (example)
from temporalio.client import Client
from fastapi import FastAPI

app = FastAPI()
temporal_client: Client = None

@app.on_event("startup")
async def startup():
    global temporal_client
    temporal_client = await Client.connect("localhost:7233")

# API endpoint (example)
@app.get("/api/releases/{release_id}")
async def get_release(release_id: str):
    service = EntityService(temporal_client)
    return await service.get_release(release_id)
```

### Alternatives Considered
1. **New client per request**: Create Temporal client for each API call
   - Rejected: Poor performance, connection overhead
2. **Sync FastAPI + threading**: Use synchronous Temporal client with thread pool
   - Rejected: Async is more efficient and Pythonic

### Best Practices
- Use FastAPI dependency injection for Temporal client
- Implement proper error handling for workflow not found, query timeouts
- Add retry logic with exponential backoff for transient Temporal connection issues
- Use structured logging to trace Temporal operations

## 3. Entity Hierarchy Retrieval Strategy

### Decision
**Parallel Query Approach**: Query parent entity first, then fan-out parallel queries for children at each level.

### Rationale
- **Performance**: Parallel queries are much faster than sequential for deep hierarchies
- **Scalability**: Handles large hierarchies (e.g., 100s of apps) efficiently
- **Simplicity**: Straightforward recursive pattern

### Implementation Pattern
```python
# Pseudocode for parallel entity retrieval
async def get_release_hierarchy(release_id: str) -> ReleaseWithChildren:
    # Step 1: Query release
    release = await query_workflow(release_id, "get_release_state")

    # Step 2: Fan-out parallel queries for all waves
    wave_tasks = [get_wave_hierarchy(wave_id) for wave_id in release.wave_ids]
    waves = await asyncio.gather(*wave_tasks)

    return ReleaseWithChildren(release=release, waves=waves)
```

### Performance Characteristics
- **Depth-5 hierarchy**: 5 sequential levels (worst case)
- **Breadth optimization**: All siblings queried in parallel
- **Typical latency**: 50-200ms for moderate hierarchy (10-50 entities)
- **Large hierarchy**: 500ms-1s for 1000 entities

### Alternatives Considered
1. **Single aggregated query**: Workflow returns entire hierarchy in one query
   - Rejected: Tightly couples workflow implementation, harder to extend
2. **Sequential queries**: Query each entity one at a time
   - Rejected: Too slow for large hierarchies (seconds instead of milliseconds)
3. **Caching layer**: Cache entity states in Redis
   - Rejected: Adds complexity, potential for stale data, violates YAGNI for initial version

## 4. Authentication Strategy

### Decision
Use JWT (JSON Web Tokens) with FastAPI's built-in security utilities. Follow patterns from fastapi/full-stack-fastapi-template.

### Rationale
- **Stateless**: JWTs don't require server-side session storage
- **Standard**: Industry-standard approach, well-supported libraries
- **Template Alignment**: Matches reference template architecture

### Implementation Pattern
- Password hashing: bcrypt via `passlib`
- Token generation: `python-jose` for JWT encoding/decoding
- FastAPI dependencies: `OAuth2PasswordBearer` for token extraction
- Token expiration: 30-minute access tokens (configurable)

### Alternatives Considered
1. **Session-based auth**: Server-side sessions with cookies
   - Rejected: Adds state management complexity, harder to scale
2. **OAuth2 external provider**: Delegate to Google/GitHub/etc.
   - Rejected: Out of scope for initial version, can add later

### Security Considerations
- Store JWT secret in environment variable, never in code
- Use HTTPS in production (terminate TLS at load balancer/ingress)
- Implement proper CORS configuration for frontend
- Log authentication failures for security monitoring

## 5. Real-time State Updates Strategy

### Decision
**Polling Approach (Initial)**: Frontend polls API every 3-5 seconds for state updates.

**Future Enhancement (P3)**: WebSocket or Server-Sent Events for push-based updates.

### Rationale for Polling
- **Simplicity**: Minimal backend complexity, reuses existing REST endpoints
- **Reliability**: HTTP polling is robust, works through all proxies/firewalls
- **Good Enough**: 3-5 second latency meets success criteria (<5s update propagation)
- **YAGNI**: Push-based updates can be added later if needed

### Implementation Pattern
```typescript
// Frontend polling hook (pseudocode)
function useReleasePolling(releaseId: string, interval = 3000) {
  const [data, setData] = useState(null);

  useEffect(() => {
    const poll = async () => {
      const response = await api.get(`/releases/${releaseId}`);
      setData(response.data);
    };

    poll(); // Initial load
    const timer = setInterval(poll, interval);
    return () => clearInterval(timer);
  }, [releaseId, interval]);

  return data;
}
```

### Alternatives Considered
1. **WebSockets**: Bi-directional realtime communication
   - Deferred: More complex, requires additional infrastructure, not needed for MVP
2. **Server-Sent Events (SSE)**: Server push over HTTP
   - Deferred: Simpler than WebSockets but still adds complexity vs. polling
3. **Long Polling**: Keep connection open until state changes
   - Rejected: More complex than regular polling, no significant benefit

### Future Enhancement Path
If real-time becomes critical (User Story 5 priority increases):
1. Add WebSocket endpoint in FastAPI using `fastapi-websockets`
2. Subscribe to Temporal workflow events to trigger push notifications
3. Implement reconnection logic in frontend

## 6. React + Chakra UI Architecture

### Decision
Use Chakra UI components with custom React hooks for data fetching. Organize by feature (pages/components/hooks).

### Rationale
- **Chakra UI Benefits**: Accessible components, theming support, responsive design out-of-box
- **Custom Hooks**: Encapsulate API calls and state management for reusability
- **Feature Organization**: Easier to navigate and maintain than type-based organization

### Component Strategy
- **ReleaseList**: Table component with sorting, displays release ID and state
- **EntityHierarchy**: Tree/nested list showing 5-level hierarchy
- **Layout**: Shared header, navigation, authentication state
- **Custom Hooks**: `useAuth`, `useReleases`, `useReleaseDetail`, `useRealtime`

### Alternatives Considered
1. **Material-UI**: Another popular component library
   - Rejected: Heavier bundle size, spec specified Chakra UI
2. **Redux for state**: Centralized state management
   - Rejected: React Query or SWR handles API state better, YAGNI for global state
3. **GraphQL**: Use GraphQL instead of REST
   - Rejected: REST is simpler, meets all requirements

### Best Practices
- Use TypeScript for type safety
- Implement error boundaries for graceful failure handling
- Use React.memo for expensive hierarchy rendering
- Lazy load pages with React.lazy and Suspense

## 7. Error Handling Strategy

### Decision
Implement structured error handling with clear user-facing messages and detailed backend logging.

### Error Categories
1. **Authentication Errors (401)**: Invalid credentials, expired token
   - User message: "Please log in again"
   - Action: Redirect to login page

2. **Authorization Errors (403)**: Insufficient permissions
   - User message: "You don't have permission to view this resource"
   - Action: Show error page

3. **Not Found Errors (404)**: Release or entity doesn't exist
   - User message: "Release not found. It may have been completed or removed."
   - Action: Show error with back button

4. **Temporal Errors**: Workflow not found, query timeout, connection issues
   - User message: "Unable to load release information. Please try again."
   - Action: Show retry button

5. **Server Errors (500)**: Unexpected backend issues
   - User message: "An unexpected error occurred. Please try again later."
   - Action: Log details, show generic error page

### Implementation Pattern
- Backend: Custom exception classes with proper HTTP status codes
- Frontend: Error boundary + toast notifications for recoverable errors
- Logging: Structured JSON logs with correlation IDs for tracing

## 8. Testing Strategy

### Decision
Multi-layer testing: unit tests (services), integration tests (Temporal queries), contract tests (API), E2E tests (user flows).

### Test Layers

**Unit Tests (pytest)**
- Entity service logic: parsing, formatting, hierarchy construction
- Authentication service: token generation, password verification
- Isolated from Temporal (use mocks)

**Integration Tests (pytest + Temporal test server)**
- Temporal query operations with real Temporal test server
- Verify query handlers return expected data
- Test error conditions (workflow not found, timeout)

**Contract Tests (pytest + OpenAPI validation)**
- Validate API responses match OpenAPI contract
- Test all endpoints with various inputs
- Verify error response formats

**E2E Tests (Playwright)**
- User Story 1: View release list
- User Story 2: Navigate to release detail
- User Story 4: Login flow
- Test with real browser, real backend, mock Temporal workflows

### Test Data Strategy
- Use factory functions to create test entities
- Mock Temporal client in unit tests
- Run real Temporal test server for integration tests
- Seed predictable data for E2E tests

### Alternatives Considered
1. **Only E2E tests**: Skip unit/integration tests
   - Rejected: E2E tests are slow, unit tests provide faster feedback
2. **Manual testing**: No automated tests
   - Rejected: Violates Constitution Principle IV (TDD)

## 9. Configuration Management

### Decision
Use Pydantic Settings for environment-based configuration. Store secrets in environment variables.

### Configuration Items
- `TEMPORAL_HOST`: Temporal server address (default: localhost:7233)
- `TEMPORAL_NAMESPACE`: Temporal namespace (default: default)
- `JWT_SECRET`: Secret for signing JWT tokens (required, no default)
- `JWT_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `API_CORS_ORIGINS`: Allowed CORS origins (default: ["http://localhost:3000"])
- `LOG_LEVEL`: Logging level (default: INFO)

### Best Practices
- Never commit secrets to git
- Use `.env` file for local development (gitignored)
- Use environment variables in production (K8s secrets, AWS Secrets Manager, etc.)
- Validate required settings on application startup

## 10. Development Workflow

### Decision
Use local Temporal CLI installation for development (not Docker). Run backend and frontend directly with native tools.

### Local Development Setup
1. **Temporal Server**: Install Temporal CLI locally (`brew install temporal` on macOS)
2. **Backend**: Python virtual environment with uvicorn hot reload
3. **Frontend**: npm dev server with hot reload
4. **Temporal UI**: Built into Temporal CLI (localhost:8080)

### Developer Experience
- Start Temporal: `temporal server start-dev`
- Start backend: `uvicorn src.main:app --reload`
- Start frontend: `npm start`
- Three terminals running, all with hot reload
- Access Temporal UI to inspect workflows
- Run tests locally with `pytest` and `npm test`

### Rationale
- **Native performance**: No Docker overhead for development
- **Simpler debugging**: Direct access to logs in terminals
- **Easier iteration**: Faster startup times than Docker containers
- **Flexible**: Can easily switch Python/Node versions
- **Industry standard**: Matches Temporal's recommended dev setup

### Alternatives Considered
1. **Docker Compose**: Container-based development environment
   - Rejected: User specifically requested local Temporal, not Docker
2. **Kubernetes for local dev**: Use Kind or Minikube
   - Rejected: Overkill for development, too complex

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Temporal Integration** | Query handlers for state retrieval | Read-only, consistent, fast, simple |
| **API Framework** | Async FastAPI with Temporal async client | Performance, clean async pattern |
| **Hierarchy Retrieval** | Parallel fan-out queries | Best performance for deep hierarchies |
| **Authentication** | JWT with FastAPI security | Stateless, standard, matches template |
| **Real-time Updates** | HTTP polling (3-5s), WebSocket future | Simple, meets requirements, extensible |
| **Frontend** | React + Chakra UI + TypeScript | Specified in requirements, good practices |
| **Error Handling** | Structured errors with user-friendly messages | Good UX, proper logging |
| **Testing** | Multi-layer: unit, integration, contract, E2E | Comprehensive coverage, fast feedback |
| **Configuration** | Pydantic Settings + env vars | Type-safe, secure, environment-aware |
| **Dev Environment** | Local Temporal CLI + native tools | Native performance, simpler debugging, matches Temporal best practices |

## Open Questions / Future Research

None - all technical decisions for initial implementation are resolved.

## References

- Temporal Python SDK: https://docs.temporal.io/dev-guide/python
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Chakra UI: https://chakra-ui.com/
- Full Stack FastAPI Template: https://github.com/fastapi/full-stack-fastapi-template
- PEP 8: https://peps.python.org/pep-0008/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
