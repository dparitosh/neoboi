import asyncio
from neo4j_service import Neo4jService

async def test_neo4j_config():
    """Test Neo4j configuration with environment settings"""
    try:
        print("Testing Neo4j Aura configuration...")
        service = Neo4jService()

        print(f"URI: {service.uri}")
        print(f"User: {service.user}")
        print(f"Database: {service.database}")

        await service.initialize_driver()
        print("✅ Neo4j connection successful!")

        # Test basic query
        result = await service.get_graph_data()
        print(f"✅ Graph data retrieved: {len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} edges")

        await service.close_driver()
        print("✅ Neo4j connection closed successfully")

    except Exception as e:
        print(f"❌ Neo4j configuration test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_neo4j_config())
    if success:
        print("\n🎉 Configuration test PASSED - Your Neo4j Aura setup is working!")
    else:
        print("\n💥 Configuration test FAILED - Check your .env.local settings")