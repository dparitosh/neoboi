import asyncio
import sys
import os
sys.path.append('.')

try:
    from neo4j_service import get_neo4j_service
    neo4j_service = get_neo4j_service()
    print('✅ Neo4j service imported successfully')
    print(f'URI: {neo4j_service.uri}')
    print(f'User: {neo4j_service.user}')
    print(f'Database: {neo4j_service.database}')
    print(f'Password set: {bool(neo4j_service.password)}')

    async def test_connection():
        try:
            print('\nTesting Neo4j connection...')
            await neo4j_service.initialize_driver()
            print('✅ Neo4j connection successful!')

            # Test the actual graph data query
            result = await neo4j_service.get_graph_data()
            print(f'✅ Graph data retrieved: {len(result.get("nodes", []))} nodes, {len(result.get("edges", []))} edges')

            # Show sample edges if any
            edges = result.get("edges", [])
            if edges:
                print('📄 Sample edges:')
                for i, edge in enumerate(edges[:5]):
                    print(f'  {i+1}. {edge.get("from", "Unknown")} -> {edge.get("label", "Unknown")} -> {edge.get("to", "Unknown")}')
            else:
                print('❌ No edges found in result')

        except Exception as e:
            print(f'❌ Neo4j connection failed: {e}')
            import traceback
            traceback.print_exc()

    asyncio.run(test_connection())

except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()