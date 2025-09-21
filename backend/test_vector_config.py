import asyncio
from neo4j_service import Neo4jService

async def test_vector_functionality():
    """Test Neo4j vector functionality"""
    try:
        print("Testing Neo4j Aura vector functionality...")
        service = Neo4jService()

        await service.initialize_driver()

        # Test vector index creation
        print("Creating vector index...")
        index_result = await service.create_vector_index()
        print(f"Vector index creation: {index_result}")

        # Test vector search (will fail without data, but tests the method)
        print("Testing vector search...")
        search_result = await service.vector_similarity_search("test query")
        print(f"Vector search result: {search_result}")

        await service.close_driver()

    except Exception as e:
        print(f"❌ Vector functionality test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_vector_functionality())
    if success:
        print("\n🎉 Vector functionality test PASSED!")
    else:
        print("\n💥 Vector functionality test FAILED")