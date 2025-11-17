"""
Test workflows for demonstrating the Temporal Release Management System.

Creates sample release workflows with the 5-level entity hierarchy:
Release → Wave → Cluster → Bundle → App

Run this script to create test releases that can be viewed in the dashboard.
"""

import asyncio
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker


# Workflow definitions
@workflow.defn
class ReleaseWorkflow:
    """
    Release workflow that maintains state for a deployment release.

    Exposes query handlers to return current state.
    """

    def __init__(self) -> None:
        self.release_id: str = ""
        self.state: str = "pending"
        self.workflow_id: str = ""
        self.wave_ids: list[str] = []
        self.created_at: str = ""
        self.updated_at: str = ""

    @workflow.run
    async def run(self, release_id: str, num_waves: int = 2) -> str:
        """
        Run the release workflow.

        Args:
            release_id: Release ID (format: release:id)
            num_waves: Number of waves to create
        """
        self.release_id = release_id
        self.workflow_id = workflow.info().workflow_id
        self.created_at = workflow.now().isoformat()
        self.updated_at = self.created_at

        # Generate wave IDs
        self.wave_ids = [f"wave:wave-{i+1}" for i in range(num_waves)]

        # Simulate release progression
        self.state = "in_progress"
        self.updated_at = workflow.now().isoformat()

        # Keep workflow running for demonstration
        # In production, this would coordinate actual deployment activities
        await workflow.sleep(3600)  # Run for 1 hour

        self.state = "completed"
        self.updated_at = workflow.now().isoformat()

        return release_id

    @workflow.query
    def get_release_state(self) -> dict:
        """Query handler to return current release state."""
        return {
            "id": self.release_id,
            "state": self.state,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "wave_ids": self.wave_ids,
        }


@workflow.defn
class WaveWorkflow:
    """Wave workflow for a deployment wave within a release."""

    def __init__(self) -> None:
        self.wave_id: str = ""
        self.state: str = "pending"
        self.release_id: str = ""
        self.sequence: int = 1
        self.cluster_ids: list[str] = []
        self.created_at: str = ""
        self.updated_at: str = ""

    @workflow.run
    async def run(self, wave_id: str, release_id: str, sequence: int, num_clusters: int = 2) -> str:
        """Run the wave workflow."""
        self.wave_id = wave_id
        self.release_id = release_id
        self.sequence = sequence
        self.created_at = workflow.now().isoformat()
        self.updated_at = self.created_at

        # Generate cluster IDs
        self.cluster_ids = [f"cluster:cluster-{sequence}-{i+1}" for i in range(num_clusters)]

        # Simulate wave progression
        await workflow.sleep(1)
        self.state = "deploying"
        self.updated_at = workflow.now().isoformat()

        await workflow.sleep(3600)  # Run for 1 hour

        self.state = "completed"
        self.updated_at = workflow.now().isoformat()

        return wave_id

    @workflow.query
    def get_wave_state(self) -> dict:
        """Query handler to return current wave state."""
        return {
            "id": self.wave_id,
            "state": self.state,
            "release_id": self.release_id,
            "sequence": self.sequence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "cluster_ids": self.cluster_ids,
        }


@workflow.defn
class ClusterWorkflow:
    """Cluster workflow for a deployment cluster within a wave."""

    def __init__(self) -> None:
        self.cluster_id: str = ""
        self.state: str = "pending"
        self.wave_id: str = ""
        self.name: str = ""
        self.bundle_id: str = ""
        self.created_at: str = ""
        self.updated_at: str = ""

    @workflow.run
    async def run(self, cluster_id: str, wave_id: str, name: str) -> str:
        """Run the cluster workflow."""
        self.cluster_id = cluster_id
        self.wave_id = wave_id
        self.name = name
        self.bundle_id = f"bundle:{cluster_id.split(':')[1]}-bundle"
        self.created_at = workflow.now().isoformat()
        self.updated_at = self.created_at

        # Simulate cluster progression
        await workflow.sleep(1)
        self.state = "deploying"
        self.updated_at = workflow.now().isoformat()

        await workflow.sleep(3600)  # Run for 1 hour

        self.state = "completed"
        self.updated_at = workflow.now().isoformat()

        return cluster_id

    @workflow.query
    def get_cluster_state(self) -> dict:
        """Query handler to return current cluster state."""
        return {
            "id": self.cluster_id,
            "state": self.state,
            "wave_id": self.wave_id,
            "name": self.name,
            "bundle_id": self.bundle_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@workflow.defn
class BundleWorkflow:
    """Bundle workflow for a deployment bundle within a cluster."""

    def __init__(self) -> None:
        self.bundle_id: str = ""
        self.state: str = "pending"
        self.cluster_id: str = ""
        self.name: str = ""
        self.app_ids: list[str] = []
        self.created_at: str = ""
        self.updated_at: str = ""

    @workflow.run
    async def run(self, bundle_id: str, cluster_id: str, name: str, num_apps: int = 3) -> str:
        """Run the bundle workflow."""
        self.bundle_id = bundle_id
        self.cluster_id = cluster_id
        self.name = name
        self.created_at = workflow.now().isoformat()
        self.updated_at = self.created_at

        # Generate app IDs
        bundle_name = bundle_id.split(':')[1]
        self.app_ids = [f"app:{bundle_name}-app-{i+1}" for i in range(num_apps)]

        # Simulate bundle progression
        await workflow.sleep(1)
        self.state = "deploying"
        self.updated_at = workflow.now().isoformat()

        await workflow.sleep(3600)  # Run for 1 hour

        self.state = "completed"
        self.updated_at = workflow.now().isoformat()

        return bundle_id

    @workflow.query
    def get_bundle_state(self) -> dict:
        """Query handler to return current bundle state."""
        return {
            "id": self.bundle_id,
            "state": self.state,
            "cluster_id": self.cluster_id,
            "name": self.name,
            "app_ids": self.app_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@workflow.defn
class AppWorkflow:
    """App workflow for an individual application within a bundle."""

    def __init__(self) -> None:
        self.app_id: str = ""
        self.state: str = "pending"
        self.bundle_id: str = ""
        self.name: str = ""
        self.version: str = "v1.0.0"
        self.created_at: str = ""
        self.updated_at: str = ""

    @workflow.run
    async def run(self, app_id: str, bundle_id: str, name: str, version: str = "v1.0.0") -> str:
        """Run the app workflow."""
        self.app_id = app_id
        self.bundle_id = bundle_id
        self.name = name
        self.version = version
        self.created_at = workflow.now().isoformat()
        self.updated_at = self.created_at

        # Simulate app deployment
        await workflow.sleep(1)
        self.state = "deploying"
        self.updated_at = workflow.now().isoformat()

        await workflow.sleep(2)
        self.state = "running"
        self.updated_at = workflow.now().isoformat()

        await workflow.sleep(3600)  # Run for 1 hour

        return app_id

    @workflow.query
    def get_app_state(self) -> dict:
        """Query handler to return current app state."""
        return {
            "id": self.app_id,
            "state": self.state,
            "bundle_id": self.bundle_id,
            "name": self.name,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# Helper functions to create test releases
async def create_test_release(client: Client, release_id: str, num_waves: int = 2) -> None:
    """
    Create a complete test release with all child entities.

    Args:
        client: Temporal client
        release_id: Release ID (format: release:id)
        num_waves: Number of waves to create
    """
    print(f"\n🚀 Creating test release: {release_id}")

    # Start release workflow
    release_handle = await client.start_workflow(
        ReleaseWorkflow.run,
        args=[release_id, num_waves],
        id=release_id,
        task_queue="release-task-queue",
    )
    print(f"✅ Started release workflow: {release_id}")

    # Create waves
    for wave_num in range(1, num_waves + 1):
        wave_id = f"wave:wave-{wave_num}"
        wave_handle = await client.start_workflow(
            WaveWorkflow.run,
            args=[wave_id, release_id, wave_num, 2],  # 2 clusters per wave
            id=wave_id,
            task_queue="release-task-queue",
        )
        print(f"  ✅ Started wave workflow: {wave_id}")

        # Create clusters for this wave
        for cluster_num in range(1, 3):  # 2 clusters per wave
            cluster_id = f"cluster:cluster-{wave_num}-{cluster_num}"
            cluster_name = f"Cluster {wave_num}-{cluster_num}"
            cluster_handle = await client.start_workflow(
                ClusterWorkflow.run,
                args=[cluster_id, wave_id, cluster_name],
                id=cluster_id,
                task_queue="release-task-queue",
            )
            print(f"    ✅ Started cluster workflow: {cluster_id}")

            # Create bundle for this cluster (exactly 1 per cluster)
            bundle_id = f"bundle:{cluster_id.split(':')[1]}-bundle"
            bundle_name = f"Bundle for {cluster_name}"
            bundle_handle = await client.start_workflow(
                BundleWorkflow.run,
                args=[bundle_id, cluster_id, bundle_name, 3],  # 3 apps per bundle
                id=bundle_id,
                task_queue="release-task-queue",
            )
            print(f"      ✅ Started bundle workflow: {bundle_id}")

            # Create apps for this bundle
            bundle_short_name = bundle_id.split(':')[1]
            for app_num in range(1, 4):  # 3 apps per bundle
                app_id = f"app:{bundle_short_name}-app-{app_num}"
                app_name = f"App {app_num} - {cluster_name}"
                app_handle = await client.start_workflow(
                    AppWorkflow.run,
                    args=[app_id, bundle_id, app_name, f"v1.{app_num}.0"],
                    id=app_id,
                    task_queue="release-task-queue",
                )
                print(f"        ✅ Started app workflow: {app_id}")

    print(f"✨ Completed creating release: {release_id}\n")


async def main() -> None:
    """
    Main function to create test workflows.

    Creates multiple test releases with the complete entity hierarchy.
    """
    print("=" * 80)
    print("🎯 Temporal Release Management System - Test Workflow Generator")
    print("=" * 80)

    # Connect to Temporal
    print("\n📡 Connecting to Temporal server...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Temporal\n")

    # Create multiple test releases
    test_releases = [
        ("release:rel-2025-01", 2),  # 2 waves
        ("release:rel-2025-02", 3),  # 3 waves
        ("release:rel-2024-12", 1),  # 1 wave
    ]

    for release_id, num_waves in test_releases:
        await create_test_release(client, release_id, num_waves)

    print("=" * 80)
    print("✅ All test workflows created successfully!")
    print("=" * 80)
    print("\n📊 Summary:")
    print(f"   • {len(test_releases)} releases created")
    print(f"   • Each release has multiple waves, clusters, bundles, and apps")
    print(f"   • View them at: http://localhost:3000")
    print(f"   • API docs at: http://localhost:8000/docs")
    print(f"   • Temporal UI at: http://localhost:8080")
    print("\n⚠️  Note: Workflows will run for 1 hour. Stop with Ctrl+C if needed.")
    print("\n🔐 Login credentials:")
    print("   • Email: admin@example.com")
    print("   • Password: admin123")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
