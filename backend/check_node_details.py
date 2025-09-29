import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from neo4j_service import get_neo4j_service

async def check_node_details():
    neo4j = get_neo4j_service()
    try:
        await neo4j.initialize_driver()
        query = 'MATCH (n) RETURN n, labels(n) as labels LIMIT 5'
        result = await neo4j.execute_query(query, {})
        print('Detailed node information:')
        for i, record in enumerate(result.get('rawRecords', [])):
            node_data = record.get('n', {})
            labels = record.get('labels', [])
            print(f'Node {i+1}:')
            print(f'  Labels: {labels}')
            print(f'  Properties: {node_data}')
            print()
        await neo4j.close_driver()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_node_details())