# Demo Guide: Temporal Release Management System

**Quick visual guide to demonstrate the system**

## 🎯 What You'll See

After following the [TESTING.md](TESTING.md) guide, you'll have a fully functional release management dashboard.

## 📸 Expected Screens

### 1. Login Page
```
┌─────────────────────────────────────────┐
│                                         │
│              Login                      │
│   Sign in to access release             │
│   management dashboard                  │
│                                         │
│   ┌────────────────────────────┐       │
│   │ Email                       │       │
│   │ admin@example.com           │       │
│   └────────────────────────────┘       │
│                                         │
│   ┌────────────────────────────┐       │
│   │ Password                    │       │
│   │ ••••••••                    │       │
│   └────────────────────────────┘       │
│                                         │
│   ┌────────────────────────────┐       │
│   │       Sign In              │       │
│   └────────────────────────────┘       │
│                                         │
│   Development credentials:              │
│   Admin: admin@example.com / admin123   │
│   User: user@example.com / user123      │
└─────────────────────────────────────────┘
```

**Test**: Login redirects you to dashboard

---

### 2. Dashboard - Release List
```
┌─────────────────────────────────────────────────────────────────┐
│ Temporal Release Manager                    admin@example.com ⚙ │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Releases                                                        │
│  View and monitor all deployment releases                       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Release ID         │ State        │ Workflow ID │ Waves    ││
│  ├────────────────────────────────────────────────────────────┤│
│  │ release:rel-2025-01│ in_progress  │ release:... │ 2        ││
│  │ release:rel-2025-02│ in_progress  │ release:... │ 3        ││
│  │ release:rel-2024-12│ in_progress  │ release:... │ 1        ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  Page 1 of 1 (3 total releases)          [Previous] [Next]     │
└─────────────────────────────────────────────────────────────────┘
```

**Test**: See all 3 test releases in the table

---

### 3. API Documentation (http://localhost:8000/docs)
```
┌─────────────────────────────────────────────────────────────────┐
│  Temporal Release Management API                   [Authorize]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ▼ Authentication                                                │
│    POST  /api/auth/login        User login                      │
│    GET   /api/auth/me           Get current user                │
│                                                                  │
│  ▼ Releases                                                      │
│    GET   /api/releases          List all releases               │
│    GET   /api/releases/{id}     Get release details             │
│                                                                  │
│  ▼ Health                                                        │
│    GET   /health                Health check                     │
│    GET   /                      Root endpoint                    │
└─────────────────────────────────────────────────────────────────┘
```

**Test**: Interactive API testing with Swagger UI

---

### 4. Temporal UI (http://localhost:8080)
```
┌─────────────────────────────────────────────────────────────────┐
│  Temporal                                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Workflows (23)                               [Filter] [Search] │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Workflow ID              │ Type            │ Status         ││
│  ├────────────────────────────────────────────────────────────┤│
│  │ release:rel-2025-01      │ ReleaseWorkflow │ Running        ││
│  │ wave:wave-1              │ WaveWorkflow    │ Running        ││
│  │ wave:wave-2              │ WaveWorkflow    │ Running        ││
│  │ cluster:cluster-1-1      │ ClusterWorkflow │ Running        ││
│  │ cluster:cluster-1-2      │ ClusterWorkflow │ Running        ││
│  │ bundle:cluster-1-1-bundle│ BundleWorkflow  │ Running        ││
│  │ app:cluster-1-1-...-app-1│ AppWorkflow     │ Running        ││
│  │ ... (16 more workflows)  │                 │                ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**Test**: See all workflows running in Temporal

---

## 🧪 Demo Scenarios

### Scenario A: New User Experience
**Duration**: 2 minutes

1. Open http://localhost:3000
2. See login page ✅
3. Enter: `user@example.com` / `user123`
4. Click "Sign In"
5. Redirected to dashboard ✅
6. See 3 releases in table ✅
7. Click user avatar → "Logout"
8. Redirected back to login ✅

**Key Points**:
- Clean, modern UI with Chakra UI
- Instant feedback (loading states)
- Secure authentication flow

---

### Scenario B: Admin Monitoring
**Duration**: 3 minutes

1. Login as admin: `admin@example.com` / `admin123`
2. View release list on dashboard
3. See state badges colored by status:
   - 🔵 Blue = "in_progress"
   - 🟢 Green = "completed"
   - 🔴 Red = "failed"
   - 🟡 Yellow = "pending"
4. Note wave counts for each release
5. Check updated timestamps

**Key Points**:
- Real-time data from Temporal workflows
- Clear visual indicators
- Comprehensive information at a glance

---

### Scenario C: API Integration
**Duration**: 3 minutes

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Expand POST /api/auth/login
4. Click "Try it out"
5. Enter credentials and execute
6. Copy `access_token` from response
7. Click "Authorize" and paste token
8. Test GET /api/releases
9. See JSON response with all releases ✅

**Key Points**:
- RESTful API design
- JWT authentication
- Interactive documentation
- Easy integration for other tools

---

### Scenario D: Workflow Deep Dive
**Duration**: 3 minutes

1. Open http://localhost:8080 (Temporal UI)
2. Click on `release:rel-2025-01` workflow
3. See workflow history/events
4. Click "Query" tab
5. Enter query name: `get_release_state`
6. Click "Query"
7. See JSON state response ✅
8. Navigate to child workflows (waves)
9. Query their states

**Key Points**:
- Direct access to workflow state
- Query handlers expose data
- Complete audit trail in Temporal

---

## 📊 Test Data Structure

After running `test_workflows.py`, you have:

### Release: rel-2025-01
```
release:rel-2025-01
├── wave:wave-1
│   ├── cluster:cluster-1-1
│   │   └── bundle:cluster-1-1-bundle
│   │       ├── app:cluster-1-1-bundle-app-1
│   │       ├── app:cluster-1-1-bundle-app-2
│   │       └── app:cluster-1-1-bundle-app-3
│   └── cluster:cluster-1-2
│       └── bundle:cluster-1-2-bundle
│           ├── app:cluster-1-2-bundle-app-1
│           ├── app:cluster-1-2-bundle-app-2
│           └── app:cluster-1-2-bundle-app-3
└── wave:wave-2
    ├── cluster:cluster-2-1
    │   └── bundle:cluster-2-1-bundle
    │       ├── app:cluster-2-1-bundle-app-1
    │       ├── app:cluster-2-1-bundle-app-2
    │       └── app:cluster-2-1-bundle-app-3
    └── cluster:cluster-2-2
        └── bundle:cluster-2-2-bundle
            ├── app:cluster-2-2-bundle-app-1
            ├── app:cluster-2-2-bundle-app-2
            └── app:cluster-2-2-bundle-app-3
```

**Total for rel-2025-01**: 1 release, 2 waves, 4 clusters, 4 bundles, 12 apps

**Similar structures for**:
- `release:rel-2025-02` (3 waves)
- `release:rel-2024-12` (1 wave)

**Grand Total**: 3 releases, 23 workflows running

---

## 🎬 Live Demo Script

### Introduction (30 seconds)
"This is a Temporal-based release management system. It tracks deployments through a 5-level hierarchy: Release → Wave → Cluster → Bundle → App. All state is stored in Temporal workflows, not a database."

### Login (15 seconds)
"First, we authenticate. The system uses JWT tokens for secure access. Let me login as admin..."

### Dashboard (1 minute)
"Here's the main dashboard. We can see 3 active releases:
- rel-2025-01 has 2 deployment waves
- rel-2025-02 has 3 waves
- rel-2024-12 has 1 wave

The state badges show each release is currently 'in_progress'. Notice the timestamps - these update in real-time as workflows progress."

### API (1 minute)
"The system exposes a REST API. Here's the interactive documentation. I'll query the releases endpoint... and we get the same data the UI shows. This API allows other tools to integrate with our release tracking."

### Temporal (1 minute)
"In the Temporal UI, we can see all the workflows. Each entity - release, wave, cluster, bundle, app - is a separate workflow. I can click into any workflow and query its current state. This is where the source of truth lives."

### Conclusion (30 seconds)
"The system provides a complete BFF (Backend for Frontend) pattern: React frontend → FastAPI backend → Temporal workflows. No database needed - Temporal handles all state management."

---

## 🔍 What to Highlight

### Technical Highlights
- ✅ **No Database**: All state in Temporal workflows
- ✅ **Query Handlers**: Direct workflow state access
- ✅ **JWT Authentication**: Secure, stateless
- ✅ **React + Chakra UI**: Modern, accessible UI
- ✅ **FastAPI + Pydantic**: Type-safe API with validation
- ✅ **Async/Await**: High performance

### Business Highlights
- ✅ **Real-time Visibility**: See deployment status instantly
- ✅ **Audit Trail**: Complete history in Temporal
- ✅ **Scalability**: Handles hundreds of concurrent deployments
- ✅ **Integration Ready**: REST API for other tools
- ✅ **Secure**: Authentication on all endpoints

---

## 💡 Pro Tips

### For Developers
```bash
# Create more test releases
python test_workflows.py  # Run multiple times

# Watch worker logs
python worker.py  # See workflow executions in real-time

# Test API with curl
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin@example.com&password=admin123" | jq -r '.access_token')

curl http://localhost:8000/api/releases \
  -H "Authorization: Bearer $TOKEN" | jq
```

### For Presenters
1. Have all 5 terminals ready before demo
2. Create test workflows in advance
3. Keep Temporal UI open in a tab
4. Prepare to show both user and admin accounts
5. Have API docs ready to demonstrate integration

---

## 🎯 Success Criteria

After the demo, viewers should understand:
- ✅ How releases are tracked (5-level hierarchy)
- ✅ Where state is stored (Temporal workflows)
- ✅ How to view releases (Web UI)
- ✅ How to integrate (REST API)
- ✅ How it scales (Multiple concurrent releases)

---

## 📚 Follow-Up Resources

- **Full Documentation**: See `specs/001-temporal-bff-system/`
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Quick Start**: [quickstart.md](specs/001-temporal-bff-system/quickstart.md)
- **Architecture**: [plan.md](specs/001-temporal-bff-system/plan.md)
- **Data Model**: [data-model.md](specs/001-temporal-bff-system/data-model.md)
