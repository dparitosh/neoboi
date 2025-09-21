import asyncio
from neo4j_service import get_neo4j_service

async def check_nodes():
    neo4j_service = get_neo4j_service()
    try:
        await neo4j_service.initialize_driver()
        data = await neo4j_service.get_graph_data()
        print('Nodes in database:')
        for i, node in enumerate(data.get('nodes', [])[:10]):  # Show first 10
            print(f'{i+1}. {node.get("label", "Unknown")} (ID: {node.get("id", "")[:8]}...) - Group: {node.get("group", "Unknown")}')

        if len(data.get('nodes', [])) > 10:
            print(f'... and {len(data.get("nodes", [])) - 10} more nodes')

        await neo4j_service.close_driver()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_nodes())