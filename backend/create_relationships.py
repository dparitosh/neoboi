import asyncio
from neo4j_service import get_neo4j_service

async def create_relationships():
    neo4j_service = get_neo4j_service()
    try:
        await neo4j_service.initialize_driver()

        # Create relationships between nodes
        relationships = [
            # DataSource -> ETLProcess relationships
            {'query': '''MATCH (ds:DataSource {name: 'Products Database'}), (etl:ETLProcess {name: 'Product Data ETL'}) CREATE (ds)-[:PROCESSES_INTO]->(etl)''', 'desc': 'Products DB -> Product ETL'},
            {'query': '''MATCH (ds:DataSource {name: 'Orders Database'}), (etl:ETLProcess {name: 'Order Processing ETL'}) CREATE (ds)-[:PROCESSES_INTO]->(etl)''', 'desc': 'Orders DB -> Order ETL'},
            {'query': '''MATCH (ds:DataSource {name: 'Legacy PLM XML Export'}), (etl:ETLProcess {name: 'Product Data ETL'}) CREATE (ds)-[:PROCESSES_INTO]->(etl)''', 'desc': 'PLM XML -> Product ETL'},

            # ETLProcess -> Service relationships
            {'query': '''MATCH (etl:ETLProcess), (svc:Service {name: 'Data Processing Service'}) WHERE etl.name CONTAINS 'ETL' CREATE (etl)-[:FEEDS_INTO]->(svc)''', 'desc': 'ETL -> Data Processing Service'},

            # Service -> Application relationships
            {'query': '''MATCH (svc:Service {name: 'Graph API Service'}), (app:Application {name: 'PLM System'}) CREATE (svc)-[:SERVES]->(app)''', 'desc': 'Graph API -> PLM System'},
            {'query': '''MATCH (svc:Service {name: 'Data Processing Service'}), (app:Application {name: 'ERP Integration'}) CREATE (svc)-[:SERVES]->(app)''', 'desc': 'Data Processing -> ERP'},

            # Application -> DataSource relationships
            {'query': '''MATCH (app:Application {name: 'PLM System'}), (ds:DataSource) WHERE ds.name CONTAINS 'PLM' OR ds.name CONTAINS 'Product' CREATE (app)-[:READS_FROM]->(ds)''', 'desc': 'PLM System reads from data sources'},
            {'query': '''MATCH (app:Application {name: 'ERP Integration'}), (ds:DataSource) WHERE ds.name CONTAINS 'Order' CREATE (app)-[:READS_FROM]->(ds)''', 'desc': 'ERP reads from order data'},

            # Neo4j relationships
            {'query': '''MATCH (ds:DataSource {name: 'Neo4j Graph DB'}), (svc:Service {name: 'Graph API Service'}) CREATE (ds)-[:STORES_DATA_FOR]->(svc)''', 'desc': 'Neo4j stores data for Graph API'},
        ]

        created_count = 0
        for rel in relationships:
            try:
                result = await neo4j_service.execute_query(rel['query'], {})
                print(f'✅ Created: {rel["desc"]}')
                created_count += 1
            except Exception as e:
                print(f'❌ Failed: {rel["desc"]} - {e}')

        print(f'\nCreated {created_count} relationships')

        # Verify the relationships were created
        data = await neo4j_service.get_graph_data()
        print(f'\nAfter creation: {len(data.get("nodes", []))} nodes, {len(data.get("edges", []))} relationships')

        await neo4j_service.close_driver()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(create_relationships())