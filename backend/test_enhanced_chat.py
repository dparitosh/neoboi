#!/usr/bin/env python3
"""
Test script for enhanced chat service with offline LLM integration
"""
import asyncio
import json
import logging
from enhanced_chat_service import enhanced_chat_service
from unstructured_pipeline.llm_service import OfflineLLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_chat():
    """Test the enhanced chat service functionality"""

    print("🧪 Testing Enhanced Chat Service with Offline LLM")
    print("=" * 60)

    # Test LLM service availability
    llm_service = OfflineLLMService()
    print(f"🔍 LLM Service Available: {llm_service.is_service_available()}")

    if not llm_service.is_service_available():
        print("❌ LLM service not available. Please start Ollama service first.")
        print("   Run: ollama serve")
        return

    # Available models
    models = llm_service.list_available_models()
    print(f"📚 Available Models: {models}")

    if not models:
        print("❌ No models available. Please pull a model first.")
        print("   Run: ollama pull llama2")
        return

    # Test queries
    test_queries = [
        "show me all suppliers",
        "analyze the graph patterns",
        "find connections between manufacturers",
        "what can you help me with?",
        "refresh the data",
        "expand the view"
    ]

    print("\n🗣️  Testing Chat Queries:")
    print("-" * 40)

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        try:
            response = await enhanced_chat_service.process_chat_query(query)
            print(f"   ✅ Response: {response.get('textResponse', '')[:100]}...")
            print(f"   📊 Graph Data: {len(response.get('graphData', {}).get('nodes', []))} nodes")
            print(f"   🎯 Confidence: {response.get('confidence', 0):.2f}")
            print(f"   🔍 Source: {response.get('source', 'unknown')}")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    # Test conversation history
    print("\n📝 Conversation History:")
    print("-" * 40)
    history = enhanced_chat_service.get_conversation_history()
    for msg in history[-3:]:  # Show last 3 messages
        print(f"   {msg['role'].title()}: {msg['content'][:50]}...")

    print("\n✅ Enhanced Chat Service Test Complete!")

async def test_llm_direct():
    """Test LLM service directly"""

    print("\n🤖 Testing LLM Service Directly:")
    print("-" * 40)

    llm_service = OfflineLLMService()

    test_prompt = "Explain how knowledge graphs work in simple terms."

    try:
        response = llm_service.generate_response(test_prompt, max_tokens=200)
        if response['success']:
            print("✅ LLM Response Generated Successfully")
            print(f"   📝 Response: {response['response'][:150]}...")
            print(".2f")
        else:
            print(f"❌ LLM Error: {response['error']}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")

async def test_chat_with_context():
    """Test chat with specific graph context"""

    print("\n🔗 Testing Chat with Graph Context:")
    print("-" * 40)

    # Mock graph context
    mock_context = {
        "nodes": [
            {"id": "1", "name": "Supplier A", "group": "Supplier"},
            {"id": "2", "name": "Manufacturer X", "group": "Manufacturer"},
            {"id": "3", "name": "Product Z", "group": "Product"}
        ],
        "edges": [
            {"source": "1", "target": "2", "label": "SUPPLIES_TO"},
            {"source": "2", "target": "3", "label": "PRODUCES"}
        ]
    }

    query = "show me the supply chain connections"
    print(f"Query: '{query}'")

    try:
        response = await enhanced_chat_service.process_chat_query(query, mock_context)
        print("✅ Context-aware response generated")
        print(f"   📊 Nodes returned: {len(response.get('graphData', {}).get('nodes', []))}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Chat Integration Tests")
    print("=" * 60)

    try:
        await test_enhanced_chat()
        await test_llm_direct()
        await test_chat_with_context()

        print("\n🎉 All tests completed!")

    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())