import asyncio
from neo4j_service import get_neo4j_service

async def create_relationships_from_nodes():
    neo4j_service = get_neo4j_service()
    try:
        await neo4j_service.initialize_driver()

        # Get all existing nodes using the same approach as get_graph_data
        driver = neo4j_service.get_driver()
        nodes_map = {}

        with driver.session(database=neo4j_service.database) as session:
            nodes_result = await asyncio.get_event_loop().run_in_executor(
                None, session.run, "MATCH (n) RETURN n LIMIT 5"
            )

            for record in nodes_result:
                n = record.get('n')
                if n:
                    node_id = n.element_id
                    labels = list(n.labels)
                    properties = dict(n.items())

                    nodes_map[node_id] = {
                        'id': node_id,
                        'labels': labels,
                        'properties': properties
                    }

        print("Nodes found:")
        for node_id, node_data in nodes_map.items():
            print(f"  ID: {node_id}")
            print(f"  Labels: {node_data['labels']}")
            print(f"  Properties keys: {list(node_data['properties'].keys())}")
            print(f"  Sample properties: {dict(list(node_data['properties'].items())[:3])}")
            print()

        # Get driver and session for creating relationships
        driver = neo4j_service.get_driver()

        with driver.session(database=neo4j_service.database) as session:
            created_relationships = 0

            for node_id, node_data in nodes_map.items():
                properties = node_data['properties']

                # Check if this node contains relationship information
                source_id = properties.get('Source Node ID')
                target_id = properties.get('Target Node ID')
                relationship_type = properties.get('Relationship')

                print(f"Processing node {node_id}:")
                print(f"  Source ID: {source_id}")
                print(f"  Target ID: {target_id}")
                print(f"  Relationship: {relationship_type}")

                if source_id and target_id and relationship_type:
                    # Create the actual relationship between source and target nodes
                    # First ensure source and target nodes exist
                    create_nodes_query = """
                    MERGE (source:Entity {id: $source_id})
                    ON CREATE SET source.type = $source_type, source.name = $source_name
                    MERGE (target:Entity {id: $target_id})
                    ON CREATE SET target.type = $target_type, target.name = $target_name
                    """

                    create_rel_query = f"""
                    MATCH (source:Entity {{id: $source_id}})
                    MATCH (target:Entity {{id: $target_id}})
                    CREATE (source)-[r:{relationship_type}]->(target)
                    RETURN r
                    """

                    params = {
                        'source_id': source_id,
                        'target_id': target_id,
                        'source_type': properties.get('Source Node Type', 'Unknown'),
                        'target_type': properties.get('Target Node Type', 'Unknown'),
                        'source_name': properties.get('Source Node Property:description', source_id),
                        'target_name': properties.get('Target Node Property: description', target_id),
                    }

                    try:
                        # First create the nodes
                        await asyncio.get_event_loop().run_in_executor(
                            None, session.run, create_nodes_query, params
                        )

                        # Then create the relationship
                        rel_result = await asyncio.get_event_loop().run_in_executor(
                            None, session.run, create_rel_query, params
                        )

                        rel_records = await asyncio.get_event_loop().run_in_executor(None, list, rel_result)
                        if rel_records:
                            created_relationships += 1
                            print(f"✅ Created relationship: {source_id} -[{relationship_type}]-> {target_id}")
                        else:
                            print(f"⚠️ No relationship created for: {source_id} -[{relationship_type}]-> {target_id}")

                    except Exception as e:
                        print(f"❌ Failed to create relationship {source_id} -> {target_id}: {e}")
                print("---")

            print(f"\nCreated {created_relationships} relationships from node data")

            # Verify relationships were created
            verify_result = await asyncio.get_event_loop().run_in_executor(
                None, session.run, "MATCH ()-[r]->() RETURN count(r) as rel_count"
            )
            verify_records = await asyncio.get_event_loop().run_in_executor(None, list, verify_result)
            rel_count = 0
            if verify_records:
                rel_count = verify_records[0].get('rel_count', 0)

            print(f"Total relationships in database: {rel_count}")

        await neo4j_service.close_driver()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(create_relationships_from_nodes())