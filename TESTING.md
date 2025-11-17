# Testing Guide: Temporal Release Management System

Complete guide for testing the system with sample workflows.

## Prerequisites

Before testing, ensure you have:

- ✅ **Temporal CLI** installed (`brew install temporal` on macOS)
- ✅ **Python 3.11+** installed
- ✅ **Node.js 18+** installed
- ✅ **Git** (to clone/navigate the repository)

## Quick Start Testing (5 Minutes)

### Step 1: Start Temporal Server

**Terminal 1:**
```bash
temporal server start-dev
```

**Expected Output:**
```
✓ Temporal server running on localhost:7233
✓ Temporal UI available at http://localhost:8080
```

✅ **Verify**: Open http://localhost:8080 - you should see the Temporal UI

---

### Step 2: Set Up Backend

**Terminal 2:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env

# IMPORTANT: Edit .env and set JWT_SECRET
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
nano .env  # or vim/code/any editor
```

**Edit `.env` file:**
```bash
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
JWT_SECRET=your-generated-secret-key-here-at-least-32-chars
JWT_EXPIRE_MINUTES=30
API_CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
```

**Start the backend:**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Temporal client connected and healthy
```

✅ **Verify**: Open http://localhost:8000/health - you should see:
```json
{
  "status": "healthy",
  "temporal": "connected",
  "api": "running"
}
```

✅ **Verify API Docs**: Open http://localhost:8000/docs - you should see interactive API documentation

---

### Step 3: Set Up Frontend

**Terminal 3:**
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start frontend
npm start
```

**Expected Output:**
```
Compiled successfully!
Local:            http://localhost:3000
```

✅ **Verify**: Open http://localhost:3000 - you should see the login page

---

### Step 4: Start Temporal Worker

**Terminal 4:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start worker
python worker.py
```

**Expected Output:**
```
================================================================================
🔧 Temporal Release Management System - Worker
================================================================================

📡 Connecting to Temporal server at localhost:7233...
✅ Connected to Temporal

🏗️  Starting worker on task queue: release-task-queue
✅ Worker started successfully
================================================================================

👂 Worker is now listening for workflow tasks...
```

✅ **Keep this running** - the worker executes workflow tasks

---

### Step 5: Create Test Workflows

**Terminal 5:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Create test releases
python test_workflows.py
```

**Expected Output:**
```
================================================================================
🎯 Temporal Release Management System - Test Workflow Generator
================================================================================

📡 Connecting to Temporal server...
✅ Connected to Temporal

🚀 Creating test release: release:rel-2025-01
✅ Started release workflow: release:rel-2025-01
  ✅ Started wave workflow: wave:wave-1
    ✅ Started cluster workflow: cluster:cluster-1-1
      ✅ Started bundle workflow: bundle:cluster-1-1-bundle
        ✅ Started app workflow: app:cluster-1-1-bundle-app-1
        ✅ Started app workflow: app:cluster-1-1-bundle-app-2
        ✅ Started app workflow: app:cluster-1-1-bundle-app-3
    ✅ Started cluster workflow: cluster:cluster-1-2
      ✅ Started bundle workflow: bundle:cluster-1-2-bundle
        ✅ Started app workflow: app:cluster-1-2-bundle-app-1
        ✅ Started app workflow: app:cluster-1-2-bundle-app-2
        ✅ Started app workflow: app:cluster-1-2-bundle-app-3
  ✅ Started wave workflow: wave:wave-2
    ... (similar output for wave 2)
✨ Completed creating release: release:rel-2025-01

... (similar output for other releases)

================================================================================
✅ All test workflows created successfully!
================================================================================

📊 Summary:
   • 3 releases created
   • Each release has multiple waves, clusters, bundles, and apps
   • View them at: http://localhost:3000
   • API docs at: http://localhost:8000/docs
   • Temporal UI at: http://localhost:8080
```

---

### Step 6: Test the Application

#### 6.1 Login

1. Open http://localhost:3000
2. You should see the login page
3. Login with:
   - **Email**: `admin@example.com`
   - **Password**: `admin123`
4. Click "Sign In"

✅ **Expected**: Redirected to dashboard with release list

---

#### 6.2 View Release List

After login, you should see the **Dashboard** with a table containing:

| Release ID | State | Workflow ID | Waves | Updated |
|------------|-------|-------------|-------|---------|
| release:rel-2025-01 | in_progress | release:rel-2025-01 | 2 | (timestamp) |
| release:rel-2025-02 | in_progress | release:rel-2025-02 | 3 | (timestamp) |
| release:rel-2024-12 | in_progress | release:rel-2024-12 | 1 | (timestamp) |

✅ **Features to Test:**
- ✅ Releases display in table
- ✅ State badges are colored (blue for "in_progress")
- ✅ Pagination controls (if more than 20 releases)
- ✅ Click on release ID is a link (will go to detail page in Phase 4)
- ✅ Header shows your email
- ✅ User menu in header (click avatar)
- ✅ Logout button works

---

#### 6.3 Test API Directly

Open http://localhost:8000/docs and test:

1. **Authorize with JWT**:
   - Click "Authorize" button
   - Login via POST /api/auth/login:
     - username: `admin@example.com`
     - password: `admin123`
   - Copy the `access_token`
   - Click "Authorize" again and paste token
   - Click "Authorize" then "Close"

2. **Test GET /api/releases**:
   - Expand GET /api/releases
   - Click "Try it out"
   - Click "Execute"
   - ✅ Should see 3 releases in response

3. **Test GET /api/releases/{release_id}**:
   - Expand GET /api/releases/{release_id}
   - Click "Try it out"
   - Enter: `release:rel-2025-01`
   - Click "Execute"
   - ✅ Should see release details with wave_ids

---

#### 6.4 View in Temporal UI

Open http://localhost:8080

1. ✅ You should see all workflows listed
2. ✅ Click on any workflow to see details
3. ✅ Click "Query" tab to test query handlers:
   - For release workflows, try: `get_release_state`
   - For wave workflows, try: `get_wave_state`
   - etc.

---

## Test Scenarios

### Scenario 1: Fresh User Login Flow

1. Clear browser localStorage (DevTools → Application → Local Storage → Clear)
2. Visit http://localhost:3000
3. ✅ Should redirect to /login
4. Enter credentials and login
5. ✅ Should see dashboard
6. ✅ Token stored in localStorage

### Scenario 2: Pagination

```bash
# Create more releases for pagination testing
cd backend
source venv/bin/activate

# Run test_workflows.py multiple times to create more releases
python test_workflows.py
python test_workflows.py
python test_workflows.py
```

Then in UI:
- ✅ See pagination controls
- ✅ Click "Next" page
- ✅ Click "Previous" page

### Scenario 3: Error Handling

**Test 1: Stop Temporal Server**
1. Stop Temporal (Ctrl+C in Terminal 1)
2. Refresh dashboard
3. ✅ Should see error message
4. ✅ "Retry" button should appear
5. Restart Temporal and click "Retry"
6. ✅ Should reload successfully

**Test 2: Invalid Token**
1. Open DevTools → Application → Local Storage
2. Edit `access_token` to invalid value
3. Refresh page
4. ✅ Should redirect to login

**Test 3: Expired Token**
1. Wait 30 minutes (or change JWT_EXPIRE_MINUTES to 1 in .env)
2. Try to fetch data
3. ✅ Should redirect to login

### Scenario 4: Multiple Users

Open in **Incognito Window**:
1. Login with: `user@example.com` / `user123`
2. ✅ Should see same releases
3. ✅ User menu shows "user@example.com"
4. ✅ No "Administrator" badge (not admin)

---

## Verification Checklist

### Backend
- [ ] Health endpoint returns 200 OK
- [ ] Auth endpoints work (login, get user)
- [ ] Release list endpoint returns data
- [ ] Individual release endpoint works
- [ ] API requires authentication (401 without token)
- [ ] Temporal client connects successfully

### Frontend
- [ ] Login page renders
- [ ] Login form submits credentials
- [ ] Dashboard loads after login
- [ ] Release table displays data
- [ ] State badges have colors
- [ ] Pagination works (if applicable)
- [ ] Logout works
- [ ] Protected routes redirect to login
- [ ] Error states display properly
- [ ] Loading spinners show during fetch

### Integration
- [ ] Backend queries Temporal workflows
- [ ] Frontend fetches from backend API
- [ ] JWT token flow works end-to-end
- [ ] Worker processes workflow tasks
- [ ] Query handlers return correct data
- [ ] Multiple workflows run concurrently

---

## Troubleshooting

### Issue: "Temporal client connection unhealthy"

**Solution:**
1. Verify Temporal is running: `lsof -i :7233`
2. Check Temporal UI: http://localhost:8080
3. Restart Temporal server

### Issue: "401 Unauthorized" on API requests

**Solution:**
1. Check JWT_SECRET is set in backend/.env
2. Verify token in localStorage
3. Try logging out and back in

### Issue: No releases showing in list

**Solution:**
1. Check worker is running (Terminal 4)
2. Run test_workflows.py again
3. Check Temporal UI for workflows
4. Look at backend logs for errors

### Issue: Frontend won't start

**Solution:**
1. Clear node_modules: `rm -rf node_modules package-lock.json`
2. Reinstall: `npm install`
3. Check Node version: `node --version` (should be 18+)

### Issue: Worker not processing tasks

**Solution:**
1. Restart worker (Ctrl+C, then `python worker.py`)
2. Check task queue name matches in workflows
3. Look for errors in worker output

---

## Stopping the System

To stop all services:

1. **Terminal 1** (Temporal): Press `Ctrl+C`
2. **Terminal 2** (Backend): Press `Ctrl+C`
3. **Terminal 3** (Frontend): Press `Ctrl+C`
4. **Terminal 4** (Worker): Press `Ctrl+C`

---

## Next Steps

After successful testing:

1. ✅ **Phase 4**: Implement release detail page with full hierarchy
2. ✅ **Phase 5**: Add individual entity query endpoints
3. ✅ **Phase 6**: Add real-time polling for auto-updates
4. ✅ **Phase 7**: Production hardening and comprehensive testing

---

## Quick Reference

| Component | URL | Credentials |
|-----------|-----|-------------|
| Frontend | http://localhost:3000 | admin@example.com / admin123 |
| Backend API | http://localhost:8000 | N/A |
| API Docs | http://localhost:8000/docs | Use JWT token |
| Health Check | http://localhost:8000/health | N/A |
| Temporal UI | http://localhost:8080 | N/A |
| Temporal Server | localhost:7233 | N/A |

---

## Support

If you encounter issues:
1. Check logs in all terminals
2. Verify all services are running
3. Review TROUBLESHOOTING section above
4. Check backend/README.md and frontend/README.md
5. Review specs/001-temporal-bff-system/ documentation
