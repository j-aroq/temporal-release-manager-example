# Testing Checklist

Use this checklist to verify the Temporal Release Management System is working correctly.

## ✅ Pre-Test Setup Verification

### Environment Check
- [ ] Python 3.11+ installed: `python --version`
- [ ] Node.js 18+ installed: `node --version`
- [ ] Temporal CLI installed: `temporal --version`
- [ ] Git repository cloned and at correct location

### File Structure Check
```bash
cd /Users/julia/dev/bff-temporal
ls -la backend/src/
ls -la frontend/src/
```

Expected directories:
- [ ] `backend/src/api/` exists
- [ ] `backend/src/core/` exists
- [ ] `backend/src/models/` exists
- [ ] `backend/src/services/` exists
- [ ] `frontend/src/components/` exists
- [ ] `frontend/src/pages/` exists
- [ ] `frontend/src/services/` exists
- [ ] `frontend/src/hooks/` exists
- [ ] `frontend/src/types/` exists

---

## 🚀 System Startup Checklist

### Terminal 1: Temporal Server
```bash
temporal server start-dev
```

**Verify:**
- [ ] Server starts without errors
- [ ] Message shows "Temporal server running on localhost:7233"
- [ ] Message shows "Temporal UI available at http://localhost:8080"
- [ ] Can access http://localhost:8080 in browser

---

### Terminal 2: Backend Setup

#### Step 1: Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**Verify:**
- [ ] Virtual environment created
- [ ] Prompt shows `(venv)` prefix

#### Step 2: Install Dependencies
```bash
pip install -e ".[dev]"
```

**Verify:**
- [ ] All packages install successfully
- [ ] No error messages
- [ ] FastAPI, temporalio, pytest installed

#### Step 3: Configure Environment
```bash
cp .env.example .env
```

**Edit .env file:**
```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Copy output and edit .env:**
```
JWT_SECRET=<paste-generated-secret-here>
```

**Verify .env file contains:**
- [ ] `TEMPORAL_HOST=localhost:7233`
- [ ] `JWT_SECRET=<32+ character string>`
- [ ] `API_CORS_ORIGINS=["http://localhost:3000"]`

#### Step 4: Start Backend
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify:**
- [ ] Server starts without errors
- [ ] Message shows "Application startup complete"
- [ ] Message shows "Temporal client connected and healthy"
- [ ] No import errors
- [ ] Can access http://localhost:8000/health

**Test Health Endpoint:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "temporal": "connected",
  "api": "running"
}
```

- [ ] Health check returns 200 OK
- [ ] All three fields show healthy status

**Test API Docs:**
- [ ] http://localhost:8000/docs loads Swagger UI
- [ ] Shows "Temporal Release Management API"
- [ ] Shows Authentication, Releases, Health sections

---

### Terminal 3: Frontend Setup

#### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

**Verify:**
- [ ] All packages install successfully
- [ ] No peer dependency errors
- [ ] `node_modules/` directory created

#### Step 2: Configure Environment
```bash
cp .env.example .env
```

**Verify .env contains:**
- [ ] `REACT_APP_API_URL=http://localhost:8000/api`

#### Step 3: Start Frontend
```bash
npm start
```

**Verify:**
- [ ] Compilation succeeds
- [ ] No TypeScript errors
- [ ] Message shows "Compiled successfully!"
- [ ] Browser opens to http://localhost:3000
- [ ] Login page displays

**Visual Check - Login Page:**
- [ ] "Login" heading visible
- [ ] Email input field present
- [ ] Password input field present
- [ ] "Sign In" button present
- [ ] Development credentials text shown at bottom

---

### Terminal 4: Worker Setup

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python worker.py
```

**Verify:**
- [ ] Worker connects to Temporal
- [ ] Message shows "Connected to Temporal"
- [ ] Message shows "Worker started successfully"
- [ ] Message shows "Worker is now listening for workflow tasks"
- [ ] Task queue: release-task-queue
- [ ] No errors

**Keep this terminal running!**

---

### Terminal 5: Create Test Workflows

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python test_workflows.py
```

**Verify:**
- [ ] Script connects to Temporal
- [ ] Creates release:rel-2025-01
- [ ] Creates release:rel-2025-02
- [ ] Creates release:rel-2024-12
- [ ] Shows "✅" checkmarks for each workflow
- [ ] Completes with "All test workflows created successfully!"
- [ ] No error messages

**Expected Output Snippet:**
```
🚀 Creating test release: release:rel-2025-01
✅ Started release workflow: release:rel-2025-01
  ✅ Started wave workflow: wave:wave-1
    ✅ Started cluster workflow: cluster:cluster-1-1
      ✅ Started bundle workflow: bundle:cluster-1-1-bundle
        ✅ Started app workflow: app:cluster-1-1-bundle-app-1
...
✨ Completed creating release: release:rel-2025-01
```

---

## 🧪 Functional Testing

### Test 1: Authentication

#### Test 1.1: Login with Valid Credentials
1. Go to http://localhost:3000
2. Enter email: `admin@example.com`
3. Enter password: `admin123`
4. Click "Sign In"

**Verify:**
- [ ] No error message appears
- [ ] Redirected to dashboard (URL changes to http://localhost:3000/)
- [ ] Dashboard loads with "Releases" heading

#### Test 1.2: Check Stored Token
1. Open DevTools (F12)
2. Go to Application → Local Storage → http://localhost:3000
3. Check for `access_token` key

**Verify:**
- [ ] `access_token` exists
- [ ] Value is a long string (JWT)
- [ ] `user` key exists with user data

#### Test 1.3: Login with Invalid Credentials
1. Logout (click avatar → Logout)
2. Try login with: `admin@example.com` / `wrongpassword`

**Verify:**
- [ ] Error message appears
- [ ] Stays on login page
- [ ] Message says "Login failed" or "Invalid email or password"

#### Test 1.4: Access Protected Route Without Auth
1. Clear localStorage (DevTools → Application → Clear)
2. Try to visit http://localhost:3000/

**Verify:**
- [ ] Redirected to /login
- [ ] Cannot access dashboard without auth

---

### Test 2: Release List Display

#### Test 2.1: View Release List
1. Login as admin
2. View dashboard

**Verify:**
- [ ] Table displays with headers: Release ID, State, Workflow ID, Waves, Updated
- [ ] Exactly 3 releases shown:
  - release:rel-2025-01
  - release:rel-2025-02
  - release:rel-2024-12
- [ ] Each has a state badge (should be blue "in_progress")
- [ ] Wave counts: 2, 3, 1 respectively
- [ ] Workflow IDs match release IDs
- [ ] Timestamps are recent

#### Test 2.2: State Badge Colors
**Verify:**
- [ ] State badges have color (not plain text)
- [ ] "in_progress" is blue
- [ ] Hover over table rows shows gray background

#### Test 2.3: Release ID Clickability
**Verify:**
- [ ] Release IDs are blue (indicating links)
- [ ] Hover shows underline
- [ ] Click is enabled (will implement detail page in Phase 4)

---

### Test 3: Header and Navigation

#### Test 3.1: Header Display
**Verify:**
- [ ] "Temporal Release Manager" title in header
- [ ] User email displayed (admin@example.com)
- [ ] Avatar icon present
- [ ] Header has white background with border

#### Test 3.2: User Menu
1. Click on avatar in header

**Verify:**
- [ ] Dropdown menu appears
- [ ] Shows user's full name ("Admin User")
- [ ] Shows email
- [ ] Shows "Administrator" badge (for admin user)
- [ ] "Logout" option in red text

#### Test 3.3: Logout
1. Click "Logout" from menu

**Verify:**
- [ ] Redirected to /login
- [ ] localStorage cleared
- [ ] Cannot go back to dashboard without re-login

---

### Test 4: API Endpoints

#### Test 4.1: GET /health
```bash
curl http://localhost:8000/health
```

**Verify:**
- [ ] Returns 200 status
- [ ] JSON with status, temporal, api fields
- [ ] All show healthy/connected/running

#### Test 4.2: POST /api/auth/login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

**Verify:**
- [ ] Returns 200 status
- [ ] JSON with access_token, token_type, expires_in
- [ ] token_type is "bearer"
- [ ] expires_in is 1800 (30 minutes)

#### Test 4.3: GET /api/releases (With Auth)
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@example.com&password=admin123" | jq -r '.access_token')

curl http://localhost:8000/api/releases \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:**
- [ ] Returns 200 status
- [ ] JSON with items array
- [ ] items contains 3 releases
- [ ] Each release has id, state, workflow_id, wave_ids

#### Test 4.4: GET /api/releases (Without Auth)
```bash
curl http://localhost:8000/api/releases
```

**Verify:**
- [ ] Returns 401 Unauthorized
- [ ] JSON with detail: "Not authenticated"

#### Test 4.5: GET /api/releases/{release_id}
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@example.com&password=admin123" | jq -r '.access_token')

curl "http://localhost:8000/api/releases/release:rel-2025-01" \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:**
- [ ] Returns 200 status
- [ ] JSON with single release object
- [ ] Has id, state, workflow_id, wave_ids
- [ ] wave_ids is array with 2 items

---

### Test 5: Temporal UI

#### Test 5.1: View Workflows
1. Go to http://localhost:8080
2. View workflows list

**Verify:**
- [ ] At least 23 workflows shown
- [ ] Release workflows visible (release:rel-2025-01, etc.)
- [ ] Wave workflows visible (wave:wave-1, etc.)
- [ ] Cluster workflows visible
- [ ] Bundle workflows visible
- [ ] App workflows visible
- [ ] All show "Running" status

#### Test 5.2: Query Workflow State
1. Click on `release:rel-2025-01` workflow
2. Click "Query" tab
3. Enter query name: `get_release_state`
4. Click "Query" button

**Verify:**
- [ ] Query succeeds
- [ ] JSON response appears
- [ ] Contains: id, state, workflow_id, wave_ids
- [ ] wave_ids has 2 items

#### Test 5.3: View Workflow History
1. Click on any workflow
2. Click "History" tab

**Verify:**
- [ ] Event list shows
- [ ] WorkflowExecutionStarted event present
- [ ] Query events may be visible if queried

---

### Test 6: Error Handling

#### Test 6.1: Backend Down
1. Stop backend (Ctrl+C in Terminal 2)
2. Try to refresh dashboard

**Verify:**
- [ ] Error message appears
- [ ] Says "Unable to retrieve releases" or similar
- [ ] "Retry" button shows
- [ ] No crash, graceful error state

3. Restart backend
4. Click "Retry"

**Verify:**
- [ ] Data loads successfully
- [ ] Error message disappears

#### Test 6.2: Temporal Down
1. Stop Temporal (Ctrl+C in Terminal 1)
2. Try to refresh dashboard

**Verify:**
- [ ] Error message appears (503 Service Unavailable)
- [ ] API returns 503 status

3. Restart Temporal
4. Wait for reconnection (~5 seconds)
5. Refresh page

**Verify:**
- [ ] Data loads successfully

#### Test 6.3: Invalid Release ID
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@example.com&password=admin123" | jq -r '.access_token')

curl "http://localhost:8000/api/releases/release:nonexistent" \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:**
- [ ] Returns 404 Not Found
- [ ] Error message mentions "Release not found"

---

### Test 7: Pagination

**Note:** With only 3 releases, pagination won't show by default (page_size=20).

**To test pagination:**
```bash
cd backend
source venv/bin/activate

# Run test_workflows.py multiple times
for i in {1..10}; do python test_workflows.py; sleep 2; done
```

Then in UI:
- [ ] More than 20 releases show pagination controls
- [ ] "Previous" button disabled on page 1
- [ ] "Next" button enabled if more pages exist
- [ ] Page counter shows correctly (e.g., "Page 1 of 2")
- [ ] Clicking "Next" loads next page

---

### Test 8: Multiple User Accounts

#### Test 8.1: Regular User
1. Logout if logged in
2. Login with: `user@example.com` / `user123`

**Verify:**
- [ ] Login succeeds
- [ ] Dashboard loads
- [ ] Same releases visible
- [ ] User menu shows "user@example.com"
- [ ] NO "Administrator" badge

#### Test 8.2: Admin User
1. Logout
2. Login with: `admin@example.com` / `admin123`

**Verify:**
- [ ] "Administrator" badge shows in user menu
- [ ] is_admin is true in user object

---

## 🔍 Integration Testing

### Test 9: End-to-End User Flow

**Full User Journey:**
1. [ ] Open http://localhost:3000 → See login
2. [ ] Enter credentials → Login succeeds
3. [ ] Dashboard loads → See 3 releases
4. [ ] Click release ID → (Will implement in Phase 4)
5. [ ] Click logout → Return to login
6. [ ] Login again → Dashboard loads again

---

### Test 10: Performance

#### Test 10.1: API Response Time
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@example.com&password=admin123" | jq -r '.access_token')

time curl -s "http://localhost:8000/api/releases" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
```

**Verify:**
- [ ] Response time < 500ms (should be ~50-200ms)

#### Test 10.2: Frontend Load Time
1. Clear browser cache
2. Open DevTools → Network tab
3. Load http://localhost:3000

**Verify:**
- [ ] Page loads in < 3 seconds
- [ ] No failed requests

---

## ✅ Final Verification

### All Services Running
- [ ] Terminal 1: Temporal server running
- [ ] Terminal 2: Backend API running (port 8000)
- [ ] Terminal 3: Frontend running (port 3000)
- [ ] Terminal 4: Worker running and listening
- [ ] Terminal 5: Test workflows created

### All URLs Accessible
- [ ] http://localhost:3000 - Frontend
- [ ] http://localhost:8000/health - Backend health
- [ ] http://localhost:8000/docs - API docs
- [ ] http://localhost:8080 - Temporal UI

### Core Features Working
- [ ] User can login
- [ ] Dashboard displays releases
- [ ] API returns data
- [ ] Workflows visible in Temporal UI
- [ ] Error handling works
- [ ] Logout works

---

## 📊 Test Results Summary

### Statistics to Record
- Number of releases displayed: _____ (expected: 3)
- Number of workflows in Temporal: _____ (expected: 23+)
- API response time: _____ ms (expected: < 500ms)
- Frontend load time: _____ seconds (expected: < 3s)

### Issues Found
List any issues encountered:

1. ________________________________
2. ________________________________
3. ________________________________

### Overall Status
- [ ] ✅ All tests passed - System ready for Phase 4
- [ ] ⚠️  Minor issues - Can proceed with caution
- [ ] ❌ Major issues - Need fixes before proceeding

---

## 🎉 Congratulations!

If all tests passed, you have:
- ✅ Working authentication system
- ✅ Functional release list display
- ✅ Temporal workflow integration
- ✅ Complete full-stack application
- ✅ Sample data for demonstration

**Ready for Phase 4: Release Details with hierarchy drill-down!**
