"""
Test the entity service list_releases method directly.
"""

import asyncio
from src.services.temporal_client import get_temporal_client
from src.services.entity_service import EntityService


async def test_list_releases():
    """Test listing releases directly."""
    print("=" * 80)
    print("🧪 Testing EntityService.list_releases()")
    print("=" * 80)

    try:
        print("\n1. Getting Temporal client...")
        client = await get_temporal_client()
        print("   ✅ Got client")

        print("\n2. Creating EntityService...")
        service = EntityService(client)
        print("   ✅ Created service")

        print("\n3. Calling list_releases()...")
        result = await service.list_releases(page=1, page_size=20)
        print(f"   ✅ Got result")

        print(f"\n📊 Results:")
        print(f"   Total: {result['total']}")
        print(f"   Page: {result['page']}")
        print(f"   Page Size: {result['page_size']}")
        print(f"   Items returned: {len(result['items'])}")

        if result['items']:
            print(f"\n📋 Releases:")
            for release in result['items']:
                print(f"   • {release.id} - State: {release.state}")
        else:
            print("\n⚠️  No releases returned (but should have found 2!)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_list_releases())
