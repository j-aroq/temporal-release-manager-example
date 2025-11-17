# Realistic Demo Releases Guide

This guide explains how to run realistic demo releases with different durations (1, 3, and 5 minutes) and different outcomes (success, failure, cancelled).

## Overview

The `demo_releases.py` script creates **3 concurrent releases** that simulate real-world deployment scenarios:

| Release | Duration | Apps | Outcome | Description |
|---------|----------|------|---------|-------------|
| **demo-1min-success** | ~1 minute | 12 | ✅ Success | All apps deploy successfully |
| **demo-3min-failure** | ~3 minutes | 12 | ❌ Failure | App-2 fails during deployment |
| **demo-5min-cancelled** | ~5 minutes | 12 | 🛑 Cancelled | Gets cancelled after 2.5 minutes |

## What's New

### Enhanced Workflow Features

The workflow (`backend/workflows.py`) now supports:

1. **Terminal States**:
   - `completed` - All entities successfully deployed
   - `failed` - One or more entities failed (error stored)
   - `cancelled` - User cancelled the release gracefully

2. **Configurable Timing**:
   - `app_deploy_time` parameter - controls deployment duration
   - Most time spent in apps (realistic simulation)
   - Minimal overhead for upper levels (0.5s each)

3. **Failure Scenarios**:
   - `"none"` - All apps succeed
   - `"app_failure"` - Specific apps fail (app-2)
   - Cancellation via signal handler

4. **Signal Handlers**:
   - `cancel_release()` - Gracefully cancels execution
   - Propagates cancellation to all entities

### Timing Breakdown

For a release with **2 waves**, **2 clusters/wave**, **3 apps/bundle** (12 total apps):

```
Total Duration = Overhead + App Processing

Overhead (fixed):
- 2 waves × 0.5s = 1s
- 4 clusters × 0.5s = 2s
- 4 bundles × 0.5s = 2s
- Total: 5 seconds

App Processing (variable - where most time is spent):
- Release 1: 12 apps × 4.58s = 55s → ~60s total (1 min)
- Release 2: 12 apps × 14.58s = 175s → ~180s total (3 min)
- Release 3: 12 apps × 24.58s = 295s → ~300s total (5 min)
```

**Key Insight**: ~90-95% of deployment time is in app processing, just like real deployments!

## Running the Demo

### Prerequisites

Ensure all services are running:

```bash
# Terminal 1: Temporal server
temporal server start-dev

# Terminal 2: Worker
cd backend
source venv/bin/activate
python worker.py
# Should see: "Worker is now listening for workflow tasks..."

# Terminal 3: Backend API
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4: Frontend
cd frontend
npm start
# Opens http://localhost:3000
```

### Launch Demo

```bash
cd backend
source venv/bin/activate
python demo_releases.py
```

## What You'll See

### 1. Script Output

```
================================================================================
🎬 DEMO: Release Deployments with Different Outcomes
================================================================================

📡 Connecting to Temporal server...
✅ Connected to Temporal

🚀 Starting all releases...

================================================================================
🚀 Starting release:demo-1min-success-173418
📝 1-minute successful deployment (all apps succeed)
⏱️  App deploy time: 4.6s per app
📊 Scenario: none
================================================================================

✅ Workflow started: release:demo-1min-success-173418
   Workflow ID: release:demo-1min-success-173418
   Expected duration: ~60s
```

### 2. Real-Time Monitoring

Every 5 seconds, the script shows progress:

```
⏰ Status at 17:34:26
--------------------------------------------------------------------------------
🔄 release:demo-1min-success-173418: in_progress
   Apps: 3 running, 1 deploying, 8 pending

🔄 release:demo-3min-failure-173418: in_progress
   Apps: 1 deploying, 11 pending

🔄 release:demo-5min-cancelled-173418: in_progress
   Apps: 1 deploying, 11 pending
--------------------------------------------------------------------------------
```

Watch as apps transition: **pending → deploying → running**

### 3. Expected Timeline

```
T+0s     All 3 releases start
T+5s     First apps start deploying
T+10s    Release 1 has 2-3 apps running
T+20s    Release 1 has 6 apps running
T+60s    ✅ Release 1 COMPLETES (all apps running)
T+90s    Release 2 has 6 apps running
T+120s   Release 3 has 4 apps running
T+150s   🛑 Release 3 CANCELLED (signal sent)
T+180s   ❌ Release 2 FAILS (app-2 error)
```

### 4. Final Summary

```
================================================================================
📊 FINAL SUMMARY
================================================================================

✅ release:demo-1min-success-173418
   State: completed
   Started: 2025-11-17T17:34:18+00:00
   Finished: 2025-11-17T17:35:18+00:00

❌ release:demo-3min-failure-173418
   State: failed
   Started: 2025-11-17T17:34:19+00:00
   Finished: 2025-11-17T17:37:19+00:00
   Error: App deployment failed: app:cluster-1-1-bundle-app-2 - Simulated failure scenario

🛑 release:demo-5min-cancelled-173418
   State: cancelled
   Started: 2025-11-17T17:34:20+00:00
   Finished: 2025-11-17T17:36:50+00:00
   Error: Release cancelled by user
================================================================================
```

## Viewing Live Progress

### Option 1: Temporal UI (http://localhost:8080)

1. Open http://localhost:8080
2. You'll see 3 new workflows:
   - `release:demo-1min-success-HHMMSS`
   - `release:demo-3min-failure-HHMMSS`
   - `release:demo-5min-cancelled-HHMMSS`
3. Click on any workflow to see:
   - **Events**: Timer events, state changes
   - **Stack Trace**: Current execution point
   - **Query Tab**: Query workflow state in real-time

**Try This**: Query `get_hierarchy` on a running workflow to see live state!

### Option 2: Frontend UI (http://localhost:3000)

1. Open http://localhost:3000
2. Login: `admin@example.com` / `admin123`
3. You'll see all releases including the 3 demo releases
4. **Click on any demo release** to see:
   - Full hierarchy tree (Release → Waves → Clusters → Bundles → Apps)
   - Real-time state updates (auto-refresh every 10 seconds)
   - Color-coded badges:
     - 🔵 Blue = in_progress / deploying
     - 🟢 Green = completed / running
     - 🔴 Red = failed
     - ⚪ Gray = pending / cancelled

**Try This**: Open a demo release and watch apps transition from pending → deploying → running in real-time!

### Option 3: Side-by-Side View (Recommended!)

Open 3 browser windows:

```
┌─────────────────┬─────────────────┬─────────────────┐
│ Temporal UI     │ Frontend List   │ Frontend Detail │
│ localhost:8080  │ localhost:3000  │ Release Page    │
│                 │                 │                 │
│ Workflow Events │ All Releases    │ Live Hierarchy  │
│ Query Interface │ State Badges    │ Auto-refresh    │
│                 │                 │ Expandable Tree │
└─────────────────┴─────────────────┴─────────────────┘
```

Watch all 3 views update simultaneously!

## Entity State Transitions

### Success Path (Release 1)

```
Release:  pending → in_progress → completed ✅
Wave:     pending → deploying → completed ✅
Cluster:  pending → deploying → completed ✅
Bundle:   pending → deploying → completed ✅
App:      pending → deploying → running ✅
```

### Failure Path (Release 2)

```
Release:  pending → in_progress → failed ❌
Wave:     pending → deploying → failed ❌
Cluster:  pending → deploying → failed ❌
Bundle:   pending → deploying → failed ❌
App-1:    pending → deploying → running ✅
App-2:    pending → deploying → failed ❌  ← Simulated failure
App-3+:   pending (never started)
```

### Cancellation Path (Release 3)

```
Release:  pending → in_progress → cancelled 🛑
Wave-1:   pending → deploying → cancelled 🛑
Apps 1-4: pending → deploying → running ✅
Apps 5+:  pending → cancelled 🛑 (never started)
```

## Understanding the Outcomes

### ✅ Success (Release 1)

- All 12 apps deploy successfully
- Each app: pending → deploying (4.6s) → running
- All parent entities complete successfully
- Final state: `completed`

### ❌ Failure (Release 2)

- Apps deploy sequentially
- When app-2 is reached (after app-1 succeeds):
  - App-2 state: deploying → failed
  - Error: "App deployment failed: app:cluster-1-1-bundle-app-2"
  - ApplicationError raised (non-retryable)
  - Error propagates up: bundle → cluster → wave → release
  - Release state: failed
  - Error message stored in release

### 🛑 Cancelled (Release 3)

- Runs for 2.5 minutes (150 seconds)
- Script sends `cancel_release` signal
- Workflow sets `cancel_requested = True`
- Next entity check sees flag and stops
- Entities already running: completed
- Entities not started: marked cancelled
- Release state: cancelled

## Customizing the Demo

Edit `backend/demo_releases.py`:

### Change Durations

```python
releases = [
    {
        "app_deploy_time": 8.0,  # Make release 1 slower (~100s)
        # ...
    }
]
```

### Change Cancellation Timing

```python
# Cancel after 1 minute instead of 2.5 minutes
asyncio.create_task(
    cancel_release_after_delay(client, cancelled_release_id, 60)
)
```

### Add More Releases

```python
releases.append({
    "id": f"release:demo-10min-{timestamp}",
    "app_deploy_time": 50.0,
    "scenario": "none",
    "description": "10-minute marathon deployment"
})
```

### Change Failure Scenario

In `workflows.py`, change which app fails:

```python
if "app-3" in app["id"]:  # Fail app-3 instead of app-2
    raise ApplicationError(...)
```

## Manual Operations

### Query a Running Workflow

```python
from temporalio.client import Client
import asyncio

async def query_release():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle("release:demo-1min-success-173418")

    # Get release state
    state = await handle.query("get_release_state")
    print(f"State: {state['state']}")

    # Get full hierarchy
    hierarchy = await handle.query("get_hierarchy")
    print(f"Waves: {len(hierarchy['waves'])}")

asyncio.run(query_release())
```

### Manually Cancel a Release

```python
async def cancel():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle("release:demo-5min-cancelled-173418")
    await handle.signal("cancel_release")
    print("Cancellation signal sent!")

asyncio.run(cancel())
```

### List All Demo Releases

```bash
python -c "
import asyncio
from temporalio.client import Client

async def list_demos():
    client = await Client.connect('localhost:7233')
    async for wf in client.list_workflows(''):
        if 'demo-' in wf.id:
            print(f'{wf.id}: {wf.status}')

asyncio.run(list_demos())
"
```

## Troubleshooting

### "Workflow already running" Error

The script uses timestamps for unique IDs. If you run it twice in the same second:
- Wait 1 second before re-running
- Or kill existing workflows in Temporal UI first

### Script Hangs with No Output

Check that the worker is running:
```bash
ps aux | grep "worker.py"
```

If not, start it:
```bash
cd backend
python worker.py
```

### Frontend Doesn't Show Demo Releases

1. Check backend is running: `curl http://localhost:8000/health`
2. Check authentication: Login again
3. Refresh the page
4. Check browser console for errors

### Workflow Fails Immediately

Check worker logs for errors:
```bash
# In the terminal running worker.py
# Look for stack traces or import errors
```

## Technical Deep Dive

### Why Most Time in Apps?

Real-world deployments:
- **Quick**: Configuration, validation, network setup
- **Slow**: Building containers, pushing images, health checks, gradual rollouts

This demo matches that pattern:
- Wave/cluster/bundle: 0.5s each (fast setup)
- Apps: 4-25s each (slow deployment)

### How Cancellation Works

1. **Signal Sent**: `handle.signal("cancel_release")`
2. **Flag Set**: `self.cancel_requested = True`
3. **Check Before Processing**: Each `_process_*` method checks flag
4. **Graceful Stop**:
   - Entities being processed: complete normally
   - Entities not started: marked "cancelled"
   - Release: completes with "cancelled" state

### How Failures Propagate

1. **Error in App**: `raise ApplicationError("...")`
2. **Caught in Bundle**: `except ApplicationError`
3. **Bundle State**: Set to "failed", re-raise
4. **Cluster Catches**: Sets state to "failed", re-raises
5. **Wave Catches**: Sets state to "failed", re-raises
6. **Release Catches**: Sets state to "failed", stores error message
7. **Workflow Completes**: With "failed" status

## Success Checklist

After running the demo, you should have:

- ✅ 3 releases with different outcomes
- ✅ Visible in Temporal UI (http://localhost:8080)
- ✅ Visible in Frontend (http://localhost:3000)
- ✅ 1 completed release (~1 min)
- ✅ 1 failed release (~3 min, app-2 error)
- ✅ 1 cancelled release (~2.5 min, user cancel)
- ✅ All states correctly reflected in hierarchy
- ✅ Error messages properly stored
- ✅ Auto-refresh showing live updates

## Next Steps

1. **Explore the Code**:
   - `backend/workflows.py` - See signal handlers and error handling
   - `backend/demo_releases.py` - Understand the demo script
   - `frontend/src/pages/ReleaseDetailPage.tsx` - Auto-refresh logic

2. **Try Variations**:
   - Run with different timings
   - Add more releases
   - Change which apps fail
   - Cancel at different times

3. **Integrate**:
   - Use the REST API to query release state
   - Build custom monitoring dashboards
   - Add alerting for failures

## Summary

This demo showcases:

- ✅ **Realistic Durations**: 1, 3, and 5-minute deployments
- ✅ **Multiple Outcomes**: Success, failure, and cancellation
- ✅ **Real-Time Visibility**: Watch state changes live
- ✅ **Graceful Cancellation**: Stop deployments cleanly
- ✅ **Error Propagation**: Failures bubble up correctly
- ✅ **Production-Like**: Most time spent in apps
- ✅ **Auto-Refresh UI**: Live updates every 10 seconds

Perfect for demonstrating real-world deployment scenarios! 🚀
