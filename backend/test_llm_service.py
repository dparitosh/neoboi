#!/usr/bin/env python3
"""
Test script for Python LLM Service
"""

import requests
import json
import time
import sys
import os

def test_python_llm_service():
    """Test the Python LLM service functionality"""

    base_url = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

    print("Testing Python LLM Service")
    print("=" * 30)

    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed")
            print(f"   Model loaded: {health_data.get('model_loaded', 'Unknown')}")
            print(f"   Device: {health_data.get('device', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test 2: Cypher generation
    print("\n2. Testing Cypher query generation...")
    test_queries = [
        "Show me all nodes",
        "Find all Person nodes",
        "Count the total number of nodes"
    ]

    for query in test_queries:
        try:
            payload = {
                "query": query,
                "context": "Neo4j graph database with nodes and relationships"
            }

            response = requests.post(
                f"{base_url}/generate-cypher",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query: '{query}'")
                print(f"   Generated: {result.get('cypher_query', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
            else:
                print(f"❌ Query failed: {query} - {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Query failed: {query} - {e}")

        time.sleep(1)  # Brief pause between requests

    # Test 3: Available models
    print("\n3. Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/models", timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            print("✅ Models endpoint working")
            print(f"   Current model: {models_data.get('current_model', 'Unknown')}")
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Models endpoint failed: {e}")

    print("\n" + "=" * 30)
    print("Test completed!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python test_llm_service.py")
        print("Tests the Python LLM service endpoints")
        sys.exit(0)

    success = test_python_llm_service()
    sys.exit(0 if success else 1)