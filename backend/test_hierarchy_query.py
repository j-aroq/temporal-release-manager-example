"""
Test the hierarchy query directly to debug the issue.
"""

import asyncio
from temporalio.client import Client


async def test_hierarchy_query():
    """Test querying hierarchy from a release workflow."""
    print("=" * 80)
    print("🔍 Testing Hierarchy Query")
    print("=" * 80)

    # Connect to Temporal
    print("\n📡 Connecting to Temporal...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected\n")

    # List workflows
    print("📋 Listing all workflows...")
    workflow_ids = []
    async for workflow in client.list_workflows(""):
        workflow_ids.append(workflow.id)
        if len(workflow_ids) >= 10:
            break

    print(f"Found {len(workflow_ids)} workflows:")
    for wf_id in workflow_ids:
        print(f"  - {wf_id}")

    # Filter for releases
    release_ids = [wf_id for wf_id in workflow_ids if wf_id.startswith("release:")]
    print(f"\n✅ Found {len(release_ids)} release workflows")

    if not release_ids:
        print("\n⚠️  No release workflows found!")
        print("   Run: python create_test_releases.py")
        return

    # Test querying the first release
    release_id = release_ids[0]
    print(f"\n🔍 Testing queries on: {release_id}")
    print("-" * 80)

    try:
        # Test get_release_state query
        print("\n1. Testing get_release_state query...")
        handle = client.get_workflow_handle(release_id)
        release_state = await handle.query("get_release_state")
        print(f"✅ get_release_state works:")
        print(f"   State: {release_state.get('state')}")
        print(f"   Wave IDs: {release_state.get('wave_ids')}")

    except Exception as e:
        print(f"❌ get_release_state failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        # Test get_hierarchy query
        print("\n2. Testing get_hierarchy query...")
        hierarchy = await handle.query("get_hierarchy")
        print(f"✅ get_hierarchy works:")
        print(f"   Release ID: {hierarchy.get('id')}")
        print(f"   State: {hierarchy.get('state')}")
        print(f"   Waves: {len(hierarchy.get('waves', []))}")

        # Check nested structure
        if hierarchy.get('waves'):
            wave = hierarchy['waves'][0]
            print(f"   First wave: {wave.get('id')} - State: {wave.get('state')}")
            if wave.get('clusters'):
                cluster = wave['clusters'][0]
                print(f"   First cluster: {cluster.get('id')} - State: {cluster.get('state')}")
                if cluster.get('bundle'):
                    bundle = cluster['bundle']
                    print(f"   Bundle: {bundle.get('id')} - State: {bundle.get('state')}")
                    if bundle.get('apps'):
                        print(f"   Apps: {len(bundle.get('apps', []))} apps")

    except Exception as e:
        print(f"❌ get_hierarchy failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        # Test get_wave_state query
        if release_state and release_state.get('wave_ids'):
            wave_id = release_state['wave_ids'][0]
            print(f"\n3. Testing get_wave_state query with wave_id: {wave_id}...")
            wave_state = await handle.query("get_wave_state", wave_id)
            if wave_state:
                print(f"✅ get_wave_state works:")
                print(f"   Wave ID: {wave_state.get('id')}")
                print(f"   State: {wave_state.get('state')}")
            else:
                print(f"❌ get_wave_state returned None")

    except Exception as e:
        print(f"❌ get_wave_state failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Testing complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_hierarchy_query())
