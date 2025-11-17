"""
Demo script to create 3 releases with different durations and outcomes.

Release 1: 1 minute - Successful completion
Release 2: 3 minutes - App failure scenario
Release 3: 5 minutes - Will be cancelled mid-execution
"""

import asyncio
from datetime import datetime
from temporalio.client import Client
from workflows import ReleaseWorkflow


async def create_release(
    client: Client,
    release_id: str,
    app_deploy_time: float,
    fail_scenario: str,
    description: str
):
    """Create a single release with specified parameters."""
    print(f"\n{'='*80}")
    print(f"🚀 Starting {release_id}")
    print(f"📝 {description}")
    print(f"⏱️  App deploy time: {app_deploy_time:.1f}s per app")
    print(f"📊 Scenario: {fail_scenario}")
    print(f"{'='*80}\n")

    try:
        handle = await client.start_workflow(
            ReleaseWorkflow.run,
            args=[
                release_id,
                2,  # num_waves
                2,  # clusters_per_wave
                3,  # apps_per_bundle
                app_deploy_time,
                fail_scenario
            ],
            id=release_id,
            task_queue="release-task-queue",
        )

        print(f"✅ Workflow started: {release_id}")
        print(f"   Workflow ID: {handle.id}")
        print(f"   Expected duration: ~{calculate_duration(app_deploy_time):.0f}s")
        return handle

    except Exception as e:
        print(f"❌ Failed to start {release_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_duration(app_deploy_time: float) -> float:
    """Calculate expected duration based on app deploy time.

    Since clusters run in PARALLEL within each wave:
    - 2 waves (sequential)
    - Each wave: 0.5s setup + max(cluster times)
    - Each cluster: 0.5s + 0.5s bundle + 3 apps × app_time
    - Clusters in a wave finish together (parallel)
    """
    num_waves = 2
    apps_per_bundle = 3
    time_per_wave = 0.5 + 0.5 + 0.5 + (apps_per_bundle * app_deploy_time)
    return num_waves * time_per_wave


async def cancel_release_after_delay(client: Client, release_id: str, delay: int):
    """Cancel a release after a delay."""
    print(f"\n⏳ Will cancel {release_id} after {delay} seconds...")
    await asyncio.sleep(delay)

    try:
        handle = client.get_workflow_handle(release_id)
        await handle.signal("cancel_release")
        print(f"🛑 Cancellation signal sent to {release_id}")
    except Exception as e:
        print(f"❌ Failed to cancel {release_id}: {e}")


async def monitor_releases(client: Client, release_ids: list[str]):
    """Monitor the progress of all releases."""
    print(f"\n{'='*80}")
    print("📊 MONITORING RELEASES")
    print(f"{'='*80}\n")

    while True:
        await asyncio.sleep(5)  # Check every 5 seconds

        print(f"\n⏰ Status at {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 80)

        all_complete = True
        for release_id in release_ids:
            try:
                handle = client.get_workflow_handle(release_id)
                state = await handle.query("get_release_state")

                # Count entity states
                all_entities = await handle.query("list_all_entities")
                app_states = {}
                for app in all_entities.get("apps", []):
                    app_state = app.get("state", "unknown")
                    app_states[app_state] = app_states.get(app_state, 0) + 1

                # Display status
                status_emoji = {
                    "pending": "⏳",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                    "cancelled": "🛑"
                }.get(state["state"], "❓")

                print(f"{status_emoji} {release_id}: {state['state']}")

                # Show app breakdown
                if app_states:
                    app_summary = ", ".join([f"{count} {state}" for state, count in app_states.items()])
                    print(f"   Apps: {app_summary}")

                # Show error if any
                if state.get("error_message"):
                    print(f"   Error: {state['error_message'][:60]}...")

                # Check if still running
                if state["state"] in ["pending", "in_progress"]:
                    all_complete = False

            except Exception as e:
                print(f"❌ {release_id}: Error querying - {str(e)[:50]}")

        print("-" * 80)

        if all_complete:
            print("\n✅ All releases have finished!")
            break


async def main():
    """Main demo script."""
    print("\n" + "="*80)
    print("🎬 DEMO: Release Deployments with Different Outcomes")
    print("="*80)

    # Connect to Temporal
    print("\n📡 Connecting to Temporal server...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Temporal\n")

    # Generate unique timestamp suffix
    timestamp = datetime.now().strftime("%H%M%S")

    # Define the 3 releases
    releases = [
        {
            "id": f"release:demo-1min-success-{timestamp}",
            "app_deploy_time": 4.58,  # ~60 seconds total
            "scenario": "none",
            "description": "1-minute successful deployment (all apps succeed)"
        },
        {
            "id": f"release:demo-3min-failure-{timestamp}",
            "app_deploy_time": 14.58,  # ~180 seconds total
            "scenario": "app_failure",
            "description": "3-minute deployment with app failure (app-2 will fail)"
        },
        {
            "id": f"release:demo-5min-cancelled-{timestamp}",
            "app_deploy_time": 24.58,  # ~300 seconds total
            "scenario": "none",
            "description": "5-minute deployment (will be cancelled after 2.5 minutes)"
        },
    ]

    # Start all releases
    print("🚀 Starting all releases...")
    release_ids = []

    for release_config in releases:
        handle = await create_release(
            client,
            release_config["id"],
            release_config["app_deploy_time"],
            release_config["scenario"],
            release_config["description"]
        )
        if handle:
            release_ids.append(release_config["id"])
        await asyncio.sleep(1)  # Small delay between starts

    if not release_ids:
        print("\n❌ No releases were started successfully!")
        return

    # Schedule cancellation for the 3rd release (after 2.5 minutes = 150 seconds)
    cancelled_release_id = f"release:demo-5min-cancelled-{timestamp}"
    asyncio.create_task(
        cancel_release_after_delay(client, cancelled_release_id, 150)
    )

    # Monitor all releases
    await monitor_releases(client, release_ids)

    # Final summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80 + "\n")

    for release_id in release_ids:
        try:
            handle = client.get_workflow_handle(release_id)
            state = await handle.query("get_release_state")

            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🛑"
            }.get(state["state"], "❓")

            print(f"{status_emoji} {release_id}")
            print(f"   State: {state['state']}")
            print(f"   Started: {state['created_at']}")
            print(f"   Finished: {state['updated_at']}")

            if state.get("error_message"):
                print(f"   Error: {state['error_message']}")

            print()

        except Exception as e:
            print(f"❌ {release_id}: Error getting final state - {e}\n")

    print("="*80)
    print("🎬 Demo complete! Check http://localhost:3000 to view in the UI")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
