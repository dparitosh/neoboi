#!/usr/bin/env python3
"""
Test script for Solr integration with Neo4j data
"""
import asyncio
import requests
import json
from solr_service import solr_service
from neo4j_service import neo4j_service

async def test_solr_integration():
    """Test the Solr integration"""
    print("🧪 Testing Solr Integration")
    print("=" * 50)

    # Test 1: Check Solr status
    try:
        stats = await solr_service.get_index_stats()
        print("✅ Solr Status Check")
        print(f"   Collection: {stats.get('collection')}")
        print(f"   Status: {stats.get('status')}")
    except Exception as e:
        print(f"❌ Solr Status Check Failed: {e}")
        return

    # Test 2: Initialize Neo4j connection
    try:
        await neo4j_service.initialize_driver()
        print("✅ Neo4j Connection Established")
    except Exception as e:
        print(f"❌ Neo4j Connection Failed: {e}")
        return

    # Test 3: Get graph data from Neo4j
    try:
        graph_data = await neo4j_service.get_graph_data()
        nodes_count = len(graph_data.get('nodes', []))
        edges_count = len(graph_data.get('edges', []))
        print("✅ Graph Data Retrieved")
        print(f"   Nodes: {nodes_count}, Edges: {edges_count}")
    except Exception as e:
        print(f"❌ Graph Data Retrieval Failed: {e}")
        return

    # Test 4: Index data into Solr
    try:
        result = await solr_service.index_graph_data(graph_data)
        print("✅ Data Indexed to Solr")
        print(f"   Nodes indexed: {result.get('nodes_indexed', 0)}")
        print(f"   Edges indexed: {result.get('edges_indexed', 0)}")
        print(f"   Total indexed: {result.get('total_indexed', 0)}")
    except Exception as e:
        print(f"❌ Data Indexing Failed: {e}")
        return

    # Test 5: Search in Solr
    try:
        search_result = await solr_service.search("supplier", limit=5)
        print("✅ Solr Search Test")
        print(f"   Query: 'supplier'")
        print(f"   Total results: {search_result.get('total', 0)}")
        print(f"   Results returned: {len(search_result.get('docs', []))}")
    except Exception as e:
        print(f"❌ Solr Search Failed: {e}")
        return

    # Test 6: Test API endpoints (if server is running)
    try:
        response = requests.get("http://127.0.0.1:3001/api/solr/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ API Endpoint Test")
            print(f"   Solr stats endpoint working")
        else:
            print("⚠️  API Endpoint Test - Server not running")
    except:
        print("⚠️  API Endpoint Test - Server not running")

    print("\n🎉 Solr Integration Test Completed!")
    print("📊 Summary:")
    print(f"   • Neo4j nodes indexed: {result.get('nodes_indexed', 0)}")
    print(f"   • Neo4j relationships indexed: {result.get('edges_indexed', 0)}")
    print(f"   • Search results for 'supplier': {search_result.get('total', 0)}")

    # Cleanup
    try:
        await neo4j_service.close_driver()
        print("✅ Neo4j connection closed")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(test_solr_integration())