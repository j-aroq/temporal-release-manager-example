"""
Temporal worker for processing release management workflows.

Runs a worker that executes the workflow definitions.
This needs to be running for workflows to progress.
"""

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

# Import unified workflow
from workflows import ReleaseWorkflow

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Main worker function.

    Connects to Temporal and starts a worker to process workflows.
    """
    print("=" * 80)
    print("🔧 Temporal Release Management System - Worker")
    print("=" * 80)

    # Connect to Temporal
    print("\n📡 Connecting to Temporal server at localhost:7233...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected to Temporal\n")

    # Create worker
    print("🏗️  Starting worker on task queue: release-task-queue")
    worker = Worker(
        client,
        task_queue="release-task-queue",
        workflows=[
            ReleaseWorkflow,  # Single unified workflow
        ],
    )

    print("✅ Worker started successfully")
    print("=" * 80)
    print("\n👂 Worker is now listening for workflow tasks...")
    print("   • Task Queue: release-task-queue")
    print("   • Workflows: ReleaseWorkflow (unified)")
    print("\n💡 Keep this running while workflows execute")
    print("   Press Ctrl+C to stop\n")
    print("=" * 80 + "\n")

    # Run worker
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
