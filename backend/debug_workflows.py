"""
Debug script to check if we can list workflows from Temporal.
"""

import asyncio
from temporalio.client import Client


async def main():
    """List all workflows and check what we get."""
    print("=" * 80)
    print("🔍 Debugging Workflow Listing")
    print("=" * 80)

    # Connect to Temporal
    print("\n📡 Connecting to Temporal at localhost:7233...")
    client = await Client.connect("localhost:7233", namespace="default")
    print("✅ Connected!\n")

    # List all workflows
    print("📋 Listing all workflows...")
    workflow_count = 0
    release_count = 0

    try:
        async for workflow in client.list_workflows(""):
            workflow_count += 1
            print(f"  {workflow_count}. ID: {workflow.id}, Status: {workflow.status}")
            if workflow.id.startswith("release:"):
                release_count += 1
    except Exception as e:
        print(f"❌ Error listing workflows: {e}")
        return

    print(f"\n📊 Summary:")
    print(f"   Total workflows: {workflow_count}")
    print(f"   Release workflows: {release_count}")

    if release_count == 0:
        print("\n⚠️  No release workflows found!")
        print("   Did you run: python test_workflows.py")
    else:
        print(f"\n✅ Found {release_count} release workflow(s)")


if __name__ == "__main__":
    asyncio.run(main())
