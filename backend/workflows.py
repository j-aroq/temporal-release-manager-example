"""
Unified Release Management Workflow.

Single workflow that manages the entire 5-level hierarchy:
Release → Wave → Cluster → Bundle → App

All entities are managed within one workflow for simplicity.
"""

import asyncio
from temporalio import workflow
from temporalio.exceptions import ApplicationError
from datetime import datetime


@workflow.defn
class ReleaseWorkflow:
    """
    Unified release workflow that manages all entities in the hierarchy.

    This single workflow contains:
    - Release (root)
    - Waves (children of release)
    - Clusters (children of waves)
    - Bundles (children of clusters)
    - Apps (children of bundles)

    Supports:
    - Configurable timing for realistic deployments
    - Failure scenarios for testing error handling
    - Cancellation via signals
    """

    def __init__(self) -> None:
        # Release-level state
        self.release_id: str = ""
        self.release_state: str = "pending"
        self.workflow_id: str = ""
        self.created_at: str = ""
        self.updated_at: str = ""
        self.error_message: str = ""

        # All child entities stored in lists
        self.waves: list[dict] = []
        self.clusters: list[dict] = []
        self.bundles: list[dict] = []
        self.apps: list[dict] = []

        # Control flags
        self.cancel_requested: bool = False
        self.fail_scenario: str = "none"  # none, app_failure, random_failure

    @workflow.run
    async def run(
        self,
        release_id: str,
        num_waves: int = 2,
        clusters_per_wave: int = 2,
        apps_per_bundle: int = 3,
        app_deploy_time: float = 4.0,
        fail_scenario: str = "none"
    ) -> str:
        """
        Run the unified release workflow.

        Args:
            release_id: Release ID (format: release:id)
            num_waves: Number of deployment waves
            clusters_per_wave: Number of clusters per wave
            apps_per_bundle: Number of apps per bundle
            app_deploy_time: Time in seconds for each app deployment (most of total time)
            fail_scenario: Failure scenario - "none", "app_failure", or "cancelled"

        Returns:
            Release ID when complete
        """
        # Initialize release
        self.release_id = release_id
        self.workflow_id = workflow.info().workflow_id
        self.created_at = workflow.now().isoformat()
        self.updated_at = self.created_at
        self.release_state = "pending"
        self.fail_scenario = fail_scenario

        # Build the entity hierarchy
        self._build_hierarchy(num_waves, clusters_per_wave, apps_per_bundle)

        # Start the release
        self.release_state = "in_progress"
        self.updated_at = workflow.now().isoformat()

        try:
            # Process each wave sequentially
            for wave in self.waves:
                # Check for cancellation
                if self.cancel_requested:
                    self.release_state = "cancelled"
                    self.updated_at = workflow.now().isoformat()
                    self.error_message = "Release cancelled by user"
                    return release_id

                await self._process_wave(wave, app_deploy_time)

            # Complete the release
            self.release_state = "completed"
            self.updated_at = workflow.now().isoformat()

        except ApplicationError as e:
            # Handle application failures
            self.release_state = "failed"
            self.error_message = str(e)
            self.updated_at = workflow.now().isoformat()
            raise

        except Exception as e:
            # Handle unexpected errors
            self.release_state = "failed"
            self.error_message = f"Unexpected error: {str(e)}"
            self.updated_at = workflow.now().isoformat()
            raise

        return release_id

    def _build_hierarchy(
        self,
        num_waves: int,
        clusters_per_wave: int,
        apps_per_bundle: int
    ) -> None:
        """Build the complete entity hierarchy."""
        now = workflow.now().isoformat()

        # Create waves
        for wave_num in range(1, num_waves + 1):
            wave_id = f"wave:wave-{wave_num}"
            wave = {
                "id": wave_id,
                "release_id": self.release_id,
                "sequence": wave_num,
                "state": "pending",
                "created_at": now,
                "updated_at": now,
                "cluster_ids": [],
            }

            # Create clusters for this wave
            for cluster_num in range(1, clusters_per_wave + 1):
                cluster_id = f"cluster:cluster-{wave_num}-{cluster_num}"
                cluster_name = f"Cluster {wave_num}-{cluster_num}"

                cluster = {
                    "id": cluster_id,
                    "wave_id": wave_id,
                    "name": cluster_name,
                    "state": "pending",
                    "created_at": now,
                    "updated_at": now,
                    "bundle_id": None,
                }

                # Create bundle for this cluster (1 bundle per cluster)
                bundle_id = f"bundle:{cluster_id.split(':')[1]}-bundle"
                bundle_name = f"Bundle for {cluster_name}"

                bundle = {
                    "id": bundle_id,
                    "cluster_id": cluster_id,
                    "name": bundle_name,
                    "state": "pending",
                    "created_at": now,
                    "updated_at": now,
                    "app_ids": [],
                }

                # Create apps for this bundle
                bundle_short_name = bundle_id.split(':')[1]
                for app_num in range(1, apps_per_bundle + 1):
                    app_id = f"app:{bundle_short_name}-app-{app_num}"
                    app_name = f"App {app_num} - {cluster_name}"

                    app = {
                        "id": app_id,
                        "bundle_id": bundle_id,
                        "name": app_name,
                        "version": f"v1.{app_num}.0",
                        "state": "pending",
                        "created_at": now,
                        "updated_at": now,
                    }

                    self.apps.append(app)
                    bundle["app_ids"].append(app_id)

                # Link bundle to cluster
                cluster["bundle_id"] = bundle_id
                self.bundles.append(bundle)
                self.clusters.append(cluster)
                wave["cluster_ids"].append(cluster_id)

            self.waves.append(wave)

    async def _process_wave(self, wave: dict, app_deploy_time: float) -> None:
        """Process a single wave (deploy all its clusters in parallel)."""
        # Check for cancellation
        if self.cancel_requested:
            wave["state"] = "cancelled"
            wave["updated_at"] = workflow.now().isoformat()
            return

        # Start wave
        wave["state"] = "deploying"
        wave["updated_at"] = workflow.now().isoformat()
        await workflow.sleep(0.5)  # Minimal wave setup time

        try:
            # Process clusters in this wave IN PARALLEL
            cluster_ids = wave["cluster_ids"]
            cluster_tasks = []

            for cluster_id in cluster_ids:
                cluster = self._find_entity(self.clusters, cluster_id)
                if cluster:
                    cluster_tasks.append(self._process_cluster(cluster, app_deploy_time))

            # Wait for all clusters to complete in parallel
            if cluster_tasks:
                await asyncio.gather(*cluster_tasks)

            # Complete wave
            wave["state"] = "completed"
            wave["updated_at"] = workflow.now().isoformat()

        except ApplicationError:
            wave["state"] = "failed"
            wave["updated_at"] = workflow.now().isoformat()
            raise

    async def _process_cluster(self, cluster: dict, app_deploy_time: float) -> None:
        """Process a single cluster (deploy its bundle)."""
        # Check for cancellation
        if self.cancel_requested:
            cluster["state"] = "cancelled"
            cluster["updated_at"] = workflow.now().isoformat()
            return

        # Start cluster
        cluster["state"] = "deploying"
        cluster["updated_at"] = workflow.now().isoformat()
        await workflow.sleep(0.5)  # Minimal cluster setup time

        try:
            # Process bundle
            bundle_id = cluster["bundle_id"]
            if bundle_id:
                bundle = self._find_entity(self.bundles, bundle_id)
                if bundle:
                    await self._process_bundle(bundle, app_deploy_time)

            # Complete cluster
            cluster["state"] = "completed"
            cluster["updated_at"] = workflow.now().isoformat()

        except ApplicationError:
            cluster["state"] = "failed"
            cluster["updated_at"] = workflow.now().isoformat()
            raise

    async def _process_bundle(self, bundle: dict, app_deploy_time: float) -> None:
        """Process a single bundle (deploy all its apps SEQUENTIALLY)."""
        # Check for cancellation
        if self.cancel_requested:
            bundle["state"] = "cancelled"
            bundle["updated_at"] = workflow.now().isoformat()
            return

        # Start bundle
        bundle["state"] = "deploying"
        bundle["updated_at"] = workflow.now().isoformat()
        await workflow.sleep(0.5)  # Minimal bundle setup time

        try:
            # Process apps SEQUENTIALLY (one after another for safety/dependencies)
            app_ids = bundle["app_ids"]
            for app_id in app_ids:
                app = self._find_entity(self.apps, app_id)
                if app:
                    await self._process_app(app, app_deploy_time)

            # Complete bundle
            bundle["state"] = "completed"
            bundle["updated_at"] = workflow.now().isoformat()

        except ApplicationError:
            bundle["state"] = "failed"
            bundle["updated_at"] = workflow.now().isoformat()
            raise

    async def _process_app(self, app: dict, app_deploy_time: float) -> None:
        """Process a single app deployment - most time spent here."""
        # Check for cancellation
        if self.cancel_requested:
            app["state"] = "cancelled"
            app["updated_at"] = workflow.now().isoformat()
            return

        # Start app deployment
        app["state"] = "deploying"
        app["updated_at"] = workflow.now().isoformat()

        # This is where most of the deployment time is spent
        await workflow.sleep(app_deploy_time)

        # Check for failure scenario
        if self.fail_scenario == "app_failure":
            # Fail specific app (e.g., app-2 in first bundle)
            if "app-2" in app["id"]:
                app["state"] = "failed"
                app["updated_at"] = workflow.now().isoformat()
                raise ApplicationError(
                    f"App deployment failed: {app['id']} - Simulated failure scenario",
                    non_retryable=True
                )

        # App deployment completed successfully
        app["state"] = "completed"
        app["updated_at"] = workflow.now().isoformat()

    def _find_entity(self, entity_list: list[dict], entity_id: str) -> dict | None:
        """Find an entity by ID in a list."""
        return next((e for e in entity_list if e["id"] == entity_id), None)

    # =========================================================================
    # Signal Handlers
    # =========================================================================

    @workflow.signal
    def cancel_release(self) -> None:
        """Signal to cancel the release workflow."""
        self.cancel_requested = True

    # =========================================================================
    # Query Handlers
    # =========================================================================

    @workflow.query
    def get_release_state(self) -> dict:
        """Get release state with wave IDs."""
        result = {
            "id": self.release_id,
            "state": self.release_state,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "wave_ids": [w["id"] for w in self.waves],
        }
        if self.error_message:
            result["error_message"] = self.error_message
        return result

    @workflow.query
    def get_wave_state(self, wave_id: str) -> dict | None:
        """Get state of a specific wave."""
        return self._find_entity(self.waves, wave_id)

    @workflow.query
    def get_cluster_state(self, cluster_id: str) -> dict | None:
        """Get state of a specific cluster."""
        return self._find_entity(self.clusters, cluster_id)

    @workflow.query
    def get_bundle_state(self, bundle_id: str) -> dict | None:
        """Get state of a specific bundle."""
        return self._find_entity(self.bundles, bundle_id)

    @workflow.query
    def get_app_state(self, app_id: str) -> dict | None:
        """Get state of a specific app."""
        return self._find_entity(self.apps, app_id)

    @workflow.query
    def get_hierarchy(self) -> dict:
        """Get complete release hierarchy with all nested entities."""
        # Build wave data with clusters
        waves_data = []

        for wave in self.waves:
            clusters_data = []

            # Add clusters for this wave
            for cluster_id in wave["cluster_ids"]:
                cluster = self._find_entity(self.clusters, cluster_id)
                if cluster:
                    bundle_data = None

                    # Add bundle for this cluster
                    bundle_id = cluster.get("bundle_id")
                    if bundle_id:
                        bundle = self._find_entity(self.bundles, bundle_id)
                        if bundle:
                            apps_data = []

                            # Add apps for this bundle
                            for app_id in bundle["app_ids"]:
                                app = self._find_entity(self.apps, app_id)
                                if app:
                                    apps_data.append(app)

                            bundle_data = {**bundle, "apps": apps_data}

                    clusters_data.append({**cluster, "bundle": bundle_data})

            waves_data.append({**wave, "clusters": clusters_data})

        # Return in the format expected by ReleaseHierarchy Pydantic model
        # The model expects { "release": {...}, "waves": [...] }
        result = {
            "id": self.release_id,
            "state": self.release_state,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "wave_ids": [w["id"] for w in self.waves],
            "waves": waves_data
        }
        if self.error_message:
            result["error_message"] = self.error_message
        return result

    @workflow.query
    def list_all_entities(self) -> dict:
        """List all entities by type (flat structure)."""
        return {
            "release": {
                "id": self.release_id,
                "state": self.release_state,
                "workflow_id": self.workflow_id,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            },
            "waves": self.waves,
            "clusters": self.clusters,
            "bundles": self.bundles,
            "apps": self.apps,
        }
