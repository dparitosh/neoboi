import asyncio
from neo4j_service import get_neo4j_service

async def check_neo4j():
    neo4j_service = get_neo4j_service()
    try:
        await neo4j_service.initialize_driver()
        result = await neo4j_service.get_graph_data()
        print(f"✅ Neo4j connected - {len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} relationships")
        await neo4j_service.close_driver()
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_neo4j())