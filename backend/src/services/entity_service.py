"""
Entity service for retrieving release management entities from Temporal workflows.

Provides methods to list releases, get individual entities, and retrieve hierarchies.
"""

import asyncio
from typing import List, Dict, Any
import logging

from ..models.entities import Release, Wave, Cluster, Bundle, App, ReleaseHierarchy
from .temporal_client import get_temporal_client, TemporalClientWrapper, WorkflowNotFoundError

logger = logging.getLogger(__name__)


class EntityNotFoundError(Exception):
    """Raised when entity is not found."""

    pass


class EntityService:
    """
    Service for retrieving entities from Temporal workflows.

    Queries workflow state via Temporal query handlers.
    """

    def __init__(self, temporal_client: TemporalClientWrapper):
        """
        Initialize entity service.

        Args:
            temporal_client: Temporal client wrapper instance
        """
        self.temporal_client = temporal_client

    async def list_releases(
        self, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List all releases with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of releases per page

        Returns:
            Dictionary with items, total, page, and page_size

        Raises:
            Exception: If listing workflows fails
        """
        try:
            # Query Temporal for all release workflows
            # In real implementation, this would filter workflows by type
            # For now, we list all workflows and filter by ID pattern
            all_workflow_ids = await self.temporal_client.list_workflows(
                query="",  # Empty query returns all workflows
                max_results=1000,  # Get up to 1000 workflows
            )

            # Filter for release workflows (ID starts with 'release:')
            release_ids = [wf_id for wf_id in all_workflow_ids if wf_id.startswith("release:")]

            # Calculate pagination
            total = len(release_ids)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_ids = release_ids[start_idx:end_idx]

            # Query each release for its state
            releases: List[Release] = []
            for release_id in paginated_ids:
                try:
                    release = await self.get_release(release_id)
                    releases.append(release)
                except Exception as e:
                    logger.error(f"Error getting release {release_id}: {e}")
                    # Continue with other releases even if one fails

            logger.info(f"Listed {len(releases)} releases (page {page}/{(total + page_size - 1) // page_size})")

            return {
                "items": releases,
                "total": total,
                "page": page,
                "page_size": page_size,
            }

        except Exception as e:
            logger.error(f"Error listing releases: {e}")
            raise

    async def get_release(self, release_id: str) -> Release:
        """
        Get single release by ID.

        Args:
            release_id: Release workflow ID (format: release:id)

        Returns:
            Release model

        Raises:
            EntityNotFoundError: If release not found
        """
        try:
            # Query workflow for release state
            result = await self.temporal_client.query_workflow(
                workflow_id=release_id,
                query_name="get_release_state",
            )

            # Also get the workflow status from Temporal
            # This handles cases where workflow was terminated externally
            workflow_status = await self.temporal_client.get_workflow_status(release_id)

            # Map Temporal status to release state if workflow was terminated/cancelled
            if workflow_status == "TERMINATED":
                result["state"] = "terminated"
            elif workflow_status == "CANCELLED":
                result["state"] = "cancelled"
            elif workflow_status == "FAILED":
                # Only override if internal state isn't already "failed"
                if result.get("state") != "failed":
                    result["state"] = "failed"
            elif workflow_status == "TIMED_OUT":
                result["state"] = "timed_out"

            # Convert query result to Release model
            release = Release(**result)
            logger.debug(f"Retrieved release: {release_id}, state: {release.state}")
            return release

        except WorkflowNotFoundError as e:
            raise EntityNotFoundError(f"Release not found: {release_id}") from e

    async def get_wave(self, wave_id: str) -> Wave:
        """
        Get single wave by ID.

        Args:
            wave_id: Wave ID (format: wave:id)

        Returns:
            Wave model

        Raises:
            EntityNotFoundError: If wave not found
        """
        try:
            # Extract release ID from wave's parent release
            # In the new structure, waves belong to a release workflow
            # We need to find which release contains this wave
            release_ids = await self._get_all_release_ids()

            for release_id in release_ids:
                try:
                    result = await self.temporal_client.query_workflow(
                        workflow_id=release_id,
                        query_name="get_wave_state",
                        args=[wave_id],  # Pass wave_id as argument
                    )
                    if result:
                        wave = Wave(**result)
                        logger.debug(f"Retrieved wave: {wave_id}")
                        return wave
                except Exception:
                    continue

            raise EntityNotFoundError(f"Wave not found: {wave_id}")

        except WorkflowNotFoundError as e:
            raise EntityNotFoundError(f"Wave not found: {wave_id}") from e

    async def get_cluster(self, cluster_id: str) -> Cluster:
        """
        Get single cluster by ID.

        Args:
            cluster_id: Cluster ID (format: cluster:id)

        Returns:
            Cluster model

        Raises:
            EntityNotFoundError: If cluster not found
        """
        try:
            # Find which release contains this cluster
            release_ids = await self._get_all_release_ids()

            for release_id in release_ids:
                try:
                    result = await self.temporal_client.query_workflow(
                        workflow_id=release_id,
                        query_name="get_cluster_state",
                        args=[cluster_id],
                    )
                    if result:
                        cluster = Cluster(**result)
                        logger.debug(f"Retrieved cluster: {cluster_id}")
                        return cluster
                except Exception:
                    continue

            raise EntityNotFoundError(f"Cluster not found: {cluster_id}")

        except WorkflowNotFoundError as e:
            raise EntityNotFoundError(f"Cluster not found: {cluster_id}") from e

    async def get_bundle(self, bundle_id: str) -> Bundle:
        """
        Get single bundle by ID.

        Args:
            bundle_id: Bundle ID (format: bundle:id)

        Returns:
            Bundle model

        Raises:
            EntityNotFoundError: If bundle not found
        """
        try:
            # Find which release contains this bundle
            release_ids = await self._get_all_release_ids()

            for release_id in release_ids:
                try:
                    result = await self.temporal_client.query_workflow(
                        workflow_id=release_id,
                        query_name="get_bundle_state",
                        args=[bundle_id],
                    )
                    if result:
                        bundle = Bundle(**result)
                        logger.debug(f"Retrieved bundle: {bundle_id}")
                        return bundle
                except Exception:
                    continue

            raise EntityNotFoundError(f"Bundle not found: {bundle_id}")

        except WorkflowNotFoundError as e:
            raise EntityNotFoundError(f"Bundle not found: {bundle_id}") from e

    async def get_app(self, app_id: str) -> App:
        """
        Get single app by ID.

        Args:
            app_id: App ID (format: app:id)

        Returns:
            App model

        Raises:
            EntityNotFoundError: If app not found
        """
        try:
            # Find which release contains this app
            release_ids = await self._get_all_release_ids()

            for release_id in release_ids:
                try:
                    result = await self.temporal_client.query_workflow(
                        workflow_id=release_id,
                        query_name="get_app_state",
                        args=[app_id],
                    )
                    if result:
                        app = App(**result)
                        logger.debug(f"Retrieved app: {app_id}")
                        return app
                except Exception:
                    continue

            raise EntityNotFoundError(f"App not found: {app_id}")

        except WorkflowNotFoundError as e:
            raise EntityNotFoundError(f"App not found: {app_id}") from e

    async def _get_all_release_ids(self) -> List[str]:
        """
        Get all release workflow IDs.

        Returns:
            List of release IDs
        """
        all_workflow_ids = await self.temporal_client.list_workflows(
            query="",
            max_results=1000,
        )
        return [wf_id for wf_id in all_workflow_ids if wf_id.startswith("release:")]

    async def get_release_hierarchy(self, release_id: str) -> ReleaseHierarchy:
        """
        Get complete release hierarchy with all child entities.

        Retrieves the full tree: Release → Waves → Clusters → Bundles → Apps
        Uses parallel queries for performance.

        Args:
            release_id: Release workflow ID (format: release:id)

        Returns:
            ReleaseHierarchy with complete nested structure

        Raises:
            EntityNotFoundError: If release not found
        """
        logger.info(f"Retrieving hierarchy for release: {release_id}")

        # Query the release workflow for complete hierarchy
        # The new unified workflow has a get_hierarchy query that returns everything
        try:
            hierarchy_dict = await self.temporal_client.query_workflow(
                workflow_id=release_id,
                query_name="get_hierarchy",
            )

            # Also check workflow status for terminated/cancelled workflows
            workflow_status = await self.temporal_client.get_workflow_status(release_id)

            # Map Temporal status to release state if workflow was terminated/cancelled
            if workflow_status == "TERMINATED":
                hierarchy_dict["state"] = "terminated"
            elif workflow_status == "CANCELLED":
                hierarchy_dict["state"] = "cancelled"
            elif workflow_status == "FAILED":
                if hierarchy_dict.get("state") != "failed":
                    hierarchy_dict["state"] = "failed"
            elif workflow_status == "TIMED_OUT":
                hierarchy_dict["state"] = "timed_out"

            hierarchy = ReleaseHierarchy(**hierarchy_dict)
            logger.info(f"Successfully retrieved hierarchy for {release_id}, state: {hierarchy.state}")
            return hierarchy

        except WorkflowNotFoundError as e:
            logger.warning(f"Release not found for hierarchy: {release_id}")
            raise EntityNotFoundError(f"Release not found: {release_id}") from e


async def get_entity_service() -> EntityService:
    """Dependency to get entity service instance."""
    temporal_client = await get_temporal_client()
    return EntityService(temporal_client)
