"""
Batch query support for efficient parallel workflow queries.

Provides utilities for querying multiple workflows in parallel.
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging

from .temporal_client import TemporalClientWrapper, WorkflowNotFoundError

logger = logging.getLogger(__name__)


async def batch_query_workflows(
    temporal_client: TemporalClientWrapper,
    workflow_ids: List[str],
    query_name: str,
    max_concurrent: int = 10,
) -> Dict[str, Any]:
    """
    Query multiple workflows in parallel with concurrency limit.

    Args:
        temporal_client: Temporal client instance
        workflow_ids: List of workflow IDs to query
        query_name: Name of the query handler
        max_concurrent: Maximum concurrent queries

    Returns:
        Dictionary mapping workflow_id to query result (or error)
    """
    results: Dict[str, Any] = {}
    semaphore = asyncio.Semaphore(max_concurrent)

    async def query_with_semaphore(workflow_id: str) -> None:
        """Query single workflow with semaphore."""
        async with semaphore:
            try:
                result = await temporal_client.query_workflow(
                    workflow_id=workflow_id,
                    query_name=query_name,
                )
                results[workflow_id] = {"success": True, "data": result}
            except WorkflowNotFoundError:
                results[workflow_id] = {"success": False, "error": "not_found"}
            except Exception as e:
                logger.error(f"Error querying workflow {workflow_id}: {e}")
                results[workflow_id] = {"success": False, "error": str(e)}

    # Create tasks for all workflows
    tasks = [query_with_semaphore(wf_id) for wf_id in workflow_ids]

    # Execute all queries in parallel (with concurrency limit)
    await asyncio.gather(*tasks)

    logger.info(
        f"Batch queried {len(workflow_ids)} workflows "
        f"({sum(1 for r in results.values() if r['success'])} successful)"
    )

    return results


async def batch_get_release_hierarchies(
    temporal_client: TemporalClientWrapper,
    release_ids: List[str],
    max_concurrent: int = 5,
) -> List[Optional[Dict[str, Any]]]:
    """
    Get hierarchies for multiple releases in parallel.

    Args:
        temporal_client: Temporal client instance
        release_ids: List of release IDs
        max_concurrent: Maximum concurrent queries

    Returns:
        List of hierarchy dictionaries (None for failed queries)
    """
    batch_results = await batch_query_workflows(
        temporal_client,
        release_ids,
        query_name="get_hierarchy",
        max_concurrent=max_concurrent,
    )

    # Convert to list maintaining order
    hierarchies = []
    for release_id in release_ids:
        result = batch_results.get(release_id)
        if result and result["success"]:
            hierarchies.append(result["data"])
        else:
            hierarchies.append(None)

    return hierarchies
