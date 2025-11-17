"""
Temporal client wrapper for querying workflow state.

Provides async methods for connecting to Temporal and querying workflow executions.
"""

import asyncio
from typing import Any, Dict, Optional
import logging

from temporalio.client import Client, WorkflowHandle
import temporalio.exceptions

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class TemporalClientError(Exception):
    """Base exception for Temporal client errors."""

    pass


class WorkflowNotFoundError(TemporalClientError):
    """Raised when workflow is not found."""

    pass


class TemporalConnectionError(TemporalClientError):
    """Raised when cannot connect to Temporal."""

    pass


class QueryTimeoutError(TemporalClientError):
    """Raised when query times out."""

    pass


class TemporalClientWrapper:
    """
    Wrapper around Temporal client for querying workflow state.

    Provides connection management, retry logic, and error handling.
    """

    def __init__(self) -> None:
        """Initialize Temporal client wrapper."""
        self.settings = get_settings()
        self._client: Optional[Client] = None
        self._connection_lock = asyncio.Lock()

    async def connect(self) -> None:
        """
        Connect to Temporal server.

        Raises:
            TemporalConnectionError: If connection fails
        """
        if self._client is not None:
            return

        async with self._connection_lock:
            # Double-check after acquiring lock
            if self._client is not None:
                return

            try:
                logger.info(
                    f"Connecting to Temporal at {self.settings.temporal_host}, "
                    f"namespace: {self.settings.temporal_namespace}"
                )
                self._client = await Client.connect(
                    self.settings.temporal_host,
                    namespace=self.settings.temporal_namespace,
                )
                logger.info("Successfully connected to Temporal")
            except Exception as e:
                logger.error(f"Failed to connect to Temporal: {e}")
                raise TemporalConnectionError(f"Failed to connect to Temporal: {e}") from e

    async def close(self) -> None:
        """Close Temporal client connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Temporal client connection closed")

    async def health_check(self) -> bool:
        """
        Check if Temporal connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            if self._client is None:
                await self.connect()
            # Try to get workflow service to verify connection
            _ = self._client.workflow_service
            return True
        except Exception as e:
            logger.error(f"Temporal health check failed: {e}")
            return False

    async def query_workflow(
        self, workflow_id: str, query_name: str, args: list = None, retry_attempts: int = 3, timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        Query a workflow execution.

        Args:
            workflow_id: Workflow execution ID
            query_name: Name of the query handler
            args: List of arguments to pass to query handler
            retry_attempts: Number of retry attempts for transient errors
            timeout: Query timeout in seconds

        Returns:
            Query result as dictionary

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist
            QueryTimeoutError: If query times out
            TemporalConnectionError: If connection fails
            TemporalClientError: For other errors
        """
        if self._client is None:
            await self.connect()

        if args is None:
            args = []

        last_exception: Optional[Exception] = None

        for attempt in range(retry_attempts):
            try:
                handle: WorkflowHandle = self._client.get_workflow_handle(workflow_id)

                # Execute query with timeout
                result = await asyncio.wait_for(
                    handle.query(query_name, *args),
                    timeout=timeout,
                )

                logger.debug(
                    f"Successfully queried workflow {workflow_id}, "
                    f"query: {query_name}, attempt: {attempt + 1}"
                )

                return result

            except asyncio.TimeoutError as e:
                logger.warning(
                    f"Query timeout for workflow {workflow_id}, "
                    f"query: {query_name}, attempt: {attempt + 1}/{retry_attempts}"
                )
                last_exception = e
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                continue

            except temporalio.exceptions.WorkflowNotFoundError as e:
                logger.error(f"Workflow not found: {workflow_id}")
                raise WorkflowNotFoundError(f"Workflow not found: {workflow_id}") from e

            except temporalio.exceptions.TemporalError as e:
                logger.warning(
                    f"Temporal error querying workflow {workflow_id}: {e}, "
                    f"attempt: {attempt + 1}/{retry_attempts}"
                )
                last_exception = e
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    # Reconnect if connection issue
                    if "unavailable" in str(e).lower() or "connection" in str(e).lower():
                        self._client = None
                        await self.connect()
                continue

            except Exception as e:
                logger.error(f"Unexpected error querying workflow {workflow_id}: {e}")
                raise TemporalClientError(
                    f"Error querying workflow {workflow_id}: {e}"
                ) from e

        # All retries exhausted
        if isinstance(last_exception, asyncio.TimeoutError):
            raise QueryTimeoutError(
                f"Query timeout after {retry_attempts} attempts for workflow {workflow_id}"
            ) from last_exception
        else:
            raise TemporalConnectionError(
                f"Failed to query workflow {workflow_id} after {retry_attempts} attempts"
            ) from last_exception

    async def get_workflow_status(self, workflow_id: str) -> str:
        """
        Get workflow execution status.

        Args:
            workflow_id: Workflow execution ID

        Returns:
            Workflow status as string: "RUNNING", "COMPLETED", "FAILED", "CANCELLED", "TERMINATED", "TIMED_OUT"

        Raises:
            WorkflowNotFoundError: If workflow doesn't exist
            TemporalConnectionError: If connection fails
        """
        if self._client is None:
            await self.connect()

        try:
            handle: WorkflowHandle = self._client.get_workflow_handle(workflow_id)
            description = await handle.describe()

            # Map Temporal status to string
            status = description.status.name  # e.g., "RUNNING", "COMPLETED", "TERMINATED", etc.

            logger.debug(f"Workflow {workflow_id} status: {status}")
            return status

        except temporalio.exceptions.WorkflowNotFoundError as e:
            logger.error(f"Workflow not found: {workflow_id}")
            raise WorkflowNotFoundError(f"Workflow not found: {workflow_id}") from e

        except Exception as e:
            logger.error(f"Error getting workflow status {workflow_id}: {e}")
            raise TemporalConnectionError(
                f"Error getting workflow status {workflow_id}: {e}"
            ) from e

    async def list_workflows(
        self,
        query: str = "",
        max_results: int = 100,
    ) -> list[str]:
        """
        List workflow IDs matching a query.

        Args:
            query: Temporal list query (empty string returns all)
            max_results: Maximum number of results to return

        Returns:
            List of workflow IDs

        Raises:
            TemporalConnectionError: If connection fails
        """
        if self._client is None:
            await self.connect()

        try:
            workflow_ids = []
            async for workflow in self._client.list_workflows(query):
                workflow_ids.append(workflow.id)
                if len(workflow_ids) >= max_results:
                    break

            logger.debug(f"Listed {len(workflow_ids)} workflows with query: '{query}'")
            return workflow_ids

        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise TemporalConnectionError(f"Error listing workflows: {e}") from e


# Global client instance
_temporal_client: Optional[TemporalClientWrapper] = None


async def get_temporal_client() -> TemporalClientWrapper:
    """Get or create global Temporal client instance."""
    global _temporal_client
    if _temporal_client is None:
        _temporal_client = TemporalClientWrapper()
        await _temporal_client.connect()
    return _temporal_client


async def close_temporal_client() -> None:
    """Close global Temporal client instance."""
    global _temporal_client
    if _temporal_client:
        await _temporal_client.close()
        _temporal_client = None
