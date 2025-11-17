"""
Create test releases using the unified ReleaseWorkflow.

This script starts release workflows that manage all entities
(waves, clusters, bundles, apps) within a single workflow.
"""

import asyncio
from datetime import datetime
from temporalio.client import Client
from workflows import ReleaseWorkflow


async def create_test_release(
    client: Client,
    release_id: str,
    num_waves: int = 2,
    clusters_per_wave: int = 2,
    apps_per_bundle: int = 3,
    app_deploy_time: float = 1.0
) -> None:
    """
    Create a test release workflow.

    Args:
        client: Temporal client
        release_id: Release ID (format: release:id)
        num_waves: Number of waves
        clusters_per_wave: Clusters per wave
        apps_per_bundle: Apps per bundle
        app_deploy_time: Time in seconds for each app deployment (default: 1.0s for fast testing)
    """
    print(f"\n🚀 Creating release: {release_id}")
    print(f"   • Waves: {num_waves}")
    print(f"   • Clusters per wave: {clusters_per_wave}")
    print(f"   • Apps per bundle: {apps_per_bundle}")
    print(f"   • App deploy time: {app_deploy_time}s")

    # Calculate total entities and estimated time
    total_clusters = num_waves * clusters_per_wave
    total_bundles = total_clusters  # 1 bundle per cluster
    total_apps = total_bundles * apps_per_bundle

    # Since clusters run in PARALLEL, time is based on longest cluster
    # Each wave: 0.5s wave setup + (0.5s cluster + 0.5s bundle + apps_per_bundle × app_time)
    # The cluster/bundle/apps time is the same for all clusters, so they finish together
    time_per_wave = 0.5 + 0.5 + 0.5 + (apps_per_bundle * app_deploy_time)
    estimated_time = num_waves * time_per_wave

    print(f"   • Total entities: {total_clusters} clusters, {total_bundles} bundles, {total_apps} apps")
    print(f"   • Estimated duration: ~{estimated_time:.0f}s")

    # Start the workflow
    handle = await client.start_workflow(
        ReleaseWorkflow.run,
        args=[release_id, num_waves, clusters_per_wave, apps_per_bundle, app_deploy_time, "none"],
        id=release_id,
        task_queue="release-task-queue",
    )

    print(f"✅ Started workflow: {release_id}")


async def main() -> None:
    """Main function to create test releases."""
    print("=" * 80)
    print("🎯 Temporal Release Management System - Test Data Generator")
    print("=" * 80)

    # Connect to Temporal
    print("\n📡 Connecting to Temporal server at localhost:7233...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Temporal\n")

    # Generate unique timestamp suffix for this run
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f"📅 Timestamp suffix: {timestamp}\n")

    # Create test releases with different configurations
    # Each release ID includes timestamp for uniqueness
    test_releases = [
        # Small release - 2 waves, quick to test
        {
            "release_id": f"release:rel-2025-01-{timestamp}",
            "num_waves": 2,
            "clusters_per_wave": 2,
            "apps_per_bundle": 3,
        },
        # Medium release - 3 waves
        {
            "release_id": f"release:rel-2025-02-{timestamp}",
            "num_waves": 3,
            "clusters_per_wave": 2,
            "apps_per_bundle": 3,
        },
        # Small single-wave release
        {
            "release_id": f"release:rel-2024-12-{timestamp}",
            "num_waves": 1,
            "clusters_per_wave": 2,
            "apps_per_bundle": 2,
        },
    ]

    for config in test_releases:
        await create_test_release(client, **config)

    print("\n" + "=" * 80)
    print("✅ All test workflows created successfully!")
    print("=" * 80)
    print("\n📊 Summary:")
    print(f"   • {len(test_releases)} releases created with unique IDs")
    print(f"   • Timestamp: {timestamp}")
    print(f"   • All entities managed within single workflows")
    print(f"   • Fast app deployment (1s per app)")
    print(f"   • Workflows will complete in ~15-30 seconds")
    print("\n🌐 Access URLs:")
    print("   • Frontend: http://localhost:3000")
    print("   • Backend API: http://localhost:8000/docs")
    print("   • Temporal UI: http://localhost:8080")
    print("\n🔐 Login Credentials:")
    print("   • Email: admin@example.com")
    print("   • Password: admin123")
    print("\n💡 Tip: Run this script multiple times - each run creates unique releases!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
