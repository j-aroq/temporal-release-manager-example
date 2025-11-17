"""
Test script to verify parallel cluster execution.

Creates a release and monitors how clusters execute - they should
run in parallel (all start at similar times) rather than sequentially.
"""

import asyncio
from datetime import datetime
from temporalio.client import Client
from workflows import ReleaseWorkflow


async def main():
    """Test parallel cluster execution."""
    print("=" * 80)
    print("🧪 Testing Parallel Cluster Execution")
    print("=" * 80)

    # Connect to Temporal
    print("\n📡 Connecting to Temporal...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected\n")

    # Create a release with multiple clusters
    timestamp = datetime.now().strftime("%H%M%S")
    release_id = f"release:parallel-test-{timestamp}"

    print(f"🚀 Starting release: {release_id}")
    print(f"   Configuration:")
    print(f"   • 1 wave")
    print(f"   • 4 clusters (should run in PARALLEL)")
    print(f"   • 2 apps per bundle")
    print(f"   • 2s per app\n")

    # Start workflow
    handle = await client.start_workflow(
        ReleaseWorkflow.run,
        args=[
            release_id,
            1,      # num_waves
            4,      # clusters_per_wave (4 clusters in parallel)
            2,      # apps_per_bundle
            2.0,    # app_deploy_time (2 seconds per app)
            "none"  # no failures
        ],
        id=release_id,
        task_queue="release-task-queue",
    )

    print("✅ Workflow started!")
    print("\n⏱️  Expected timing:")
    print("   • Sequential (OLD): ~20s (4 clusters × 5s each)")
    print("   • Parallel (NEW): ~6s (all clusters finish together)")
    print("\n⏳ Monitoring execution...\n")

    # Monitor progress
    start_time = datetime.now()
    last_states = {}

    while True:
        await asyncio.sleep(1)

        try:
            # Get all entities
            all_entities = await handle.query("list_all_entities")
            release = all_entities.get("release", {})
            clusters = all_entities.get("clusters", [])

            elapsed = (datetime.now() - start_time).total_seconds()

            # Check cluster states
            cluster_states = {}
            for cluster in clusters:
                cluster_id = cluster.get("id", "").split(":")[-1]
                state = cluster.get("state", "unknown")
                cluster_states[cluster_id] = state

            # Detect when clusters change state together (parallel execution)
            if cluster_states != last_states:
                print(f"[{elapsed:5.1f}s] Cluster states: {cluster_states}")
                last_states = cluster_states.copy()

            # Check if release is complete
            if release.get("state") in ["completed", "failed", "cancelled"]:
                print(f"\n✅ Release {release.get('state')} in {elapsed:.1f}s")
                break

        except Exception as e:
            print(f"Error querying: {e}")
            break

    # Analyze results
    print("\n" + "=" * 80)
    print("📊 Analysis")
    print("=" * 80)

    all_entities = await handle.query("list_all_entities")
    clusters = all_entities.get("clusters", [])

    print(f"\n🔍 Cluster execution pattern:")
    for cluster in clusters:
        cluster_id = cluster.get("id", "")
        state = cluster.get("state", "")
        print(f"   • {cluster_id}: {state}")

    if elapsed < 12:
        print(f"\n✅ SUCCESS! Completed in {elapsed:.1f}s")
        print("   Clusters ran in PARALLEL (expected ~6s)")
    else:
        print(f"\n⚠️  SLOW! Completed in {elapsed:.1f}s")
        print("   Clusters may have run SEQUENTIALLY (would take ~20s)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
