import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from neo4j_service import Neo4jService

async def test_connection():
    try:
        print("Testing Neo4j Aura connection...")
        neo4j_service = Neo4jService()
        await neo4j_service.initialize_driver()
        print('✅ Neo4j Aura connection successful')

        # Test a simple query
        driver = neo4j_service.get_driver()
        with driver.session(database=neo4j_service.database) as session:
            result = await asyncio.get_event_loop().run_in_executor(
                None, session.run, "RETURN 'Hello from Neo4j Aura!' as message"
            )
            record = await asyncio.get_event_loop().run_in_executor(None, result.single)
            print(f'✅ Query test result: {record["message"]}')

    except Exception as e:
        print(f'❌ Neo4j Aura connection failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())