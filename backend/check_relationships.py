import asyncio
from neo4j_service import get_neo4j_service

async def check_relationships():
    neo4j_service = get_neo4j_service()
    try:
        await neo4j_service.initialize_driver()
        driver = neo4j_service.get_driver()

        with driver.session(database=neo4j_service.database) as session:
            # Check relationship count
            result1 = session.run('MATCH ()-[r]-() RETURN count(r) as relationship_count')
            count_record = result1.single()
            print(f'Total relationships in database: {count_record["relationship_count"]}')

            # Check relationship types
            result2 = session.run('MATCH ()-[r]-() RETURN type(r) as rel_type, count(r) as count ORDER BY count DESC LIMIT 10')
            print('Relationship types:')
            for record in result2:
                print(f'  {record["rel_type"]}: {record["count"]}')

            # Check a few actual relationships
            result3 = session.run('MATCH (n)-[r]-(m) RETURN n.name, type(r), m.name LIMIT 5')
            print('Sample relationships:')
            for record in result3:
                print(f'  {record["n.name"]} -[{record["type(r)"]}]-> {record["m.name"]}')

        await neo4j_service.close_driver()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_relationships())