import asyncio
from neo4j_service import get_neo4j_service

async def debug_relationships():
    neo4j_service = get_neo4j_service()
    try:
        await neo4j_service.initialize_driver()
        driver = neo4j_service.get_driver()

        with driver.session(database=neo4j_service.database) as session:
            # Check what relationships look like
            result = session.run('MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 3')
            print('Sample relationship records:')
            for i, record in enumerate(result):
                n = record.get('n')
                r = record.get('r')
                m = record.get('m')
                print(f'Record {i+1}:')
                print(f'  n: element_id={n.element_id if n else None}, labels={list(n.labels) if n else None}')
                print(f'  r: element_id={r.element_id if r else None}, type={r.type if r else None}')
                print(f'  m: element_id={m.element_id if m else None}, labels={list(m.labels) if m else None}')
                print()

        await neo4j_service.close_driver()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(debug_relationships())