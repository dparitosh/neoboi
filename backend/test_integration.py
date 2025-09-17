#!/usr/bin/env python3
"""
Test script to verify Python backend and frontend integration
"""
import requests
import json
import time

def test_backend_integration():
    """Test the Python backend API endpoints"""
    base_url = "http://127.0.0.1:3001"

    print("🧪 Testing Python Backend Integration")
    print("=" * 50)

    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Neo4j connected: {health_data.get('neo4j_connected')}")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")

    # Test 2: Graph API
    try:
        response = requests.get(f"{base_url}/api/graph")
        if response.status_code == 200:
            graph_data = response.json()
            nodes_count = len(graph_data.get('nodes', []))
            edges_count = len(graph_data.get('edges', []))
            print("✅ Graph API working")
            print(f"   Nodes: {nodes_count}, Edges: {edges_count}")
        else:
            print("❌ Graph API failed")
    except Exception as e:
        print(f"❌ Graph API error: {e}")

    # Test 3: Chat API
    try:
        chat_payload = {"query": "show me suppliers"}
        response = requests.post(f"{base_url}/api/chat", json=chat_payload)
        if response.status_code == 200:
            chat_data = response.json()
            print("✅ Chat API working")
            print(f"   Response: {chat_data.get('textResponse', '')[:50]}...")
        else:
            print("❌ Chat API failed")
    except Exception as e:
        print(f"❌ Chat API error: {e}")

    # Test 4: Frontend serving
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200 and "Neo4j Graph Visualization" in response.text:
            print("✅ Frontend serving working")
        else:
            print("❌ Frontend serving failed")
    except Exception as e:
        print(f"❌ Frontend serving error: {e}")

    print("\n🎉 Backend integration test completed!")
    print("📱 Frontend should be accessible at: http://127.0.0.1:3001/")

if __name__ == "__main__":
    test_backend_integration()