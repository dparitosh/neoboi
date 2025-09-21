import asyncio
from neo4j_service import neo4j_service

async def test_neo4j():
    try:
        print('Testing Neo4j connection...')
        await neo4j_service.initialize_driver()
        print('Neo4j initialized successfully')

        # Test getting graph data
        data = await neo4j_service.get_graph_data()
        print(f'Graph data retrieved: {len(data.get("nodes", []))} nodes, {len(data.get("edges", []))} edges')

    except Exception as e:
        print(f'Neo4j test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_neo4j())