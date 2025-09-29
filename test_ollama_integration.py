#!/usr/bin/env python3
"""
Test OLLAMA integration to verify it's working correctly
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.unstructured_pipeline.llm_service import OfflineLLMService
from backend.config import get_settings

async def test_ollama_integration():
    """Test OLLAMA service integration"""
    print("🧪 Testing OLLAMA Integration...")
    
    # Initialize the service
    try:
        settings = get_settings()
        print(f"📡 OLLAMA Host: {settings.ollama_host}")
        print(f"🤖 Default Model: {settings.ollama_default_model}")
        
        llm_service = OfflineLLMService()
        
        # Test 1: Check if service is available
        print("\n1️⃣ Testing service availability...")
        is_available = llm_service.is_service_available()
        print(f"   ✅ Service Available: {is_available}")
        
        if not is_available:
            print("❌ OLLAMA service is not available. Please check if it's running.")
            return False
            
        # Test 2: List available models
        print("\n2️⃣ Testing model listing...")
        models = llm_service.list_available_models()
        print(f"   ✅ Available Models: {models}")
        
        # Test 3: Simple text generation
        print("\n3️⃣ Testing text generation...")
        test_prompt = "What is artificial intelligence? Please provide a brief explanation."
        response = llm_service.generate_response(test_prompt, max_tokens=100)
        
        if response['success']:
            print(f"   ✅ Generation Success: True")
            print(f"   📝 Response: {response['response'][:200]}...")
            print(f"   🤖 Model Used: {response['model']}")
            print(f"   ⏱️ Duration: {response.get('total_duration', 0) / 1e9:.2f}s")
        else:
            print(f"   ❌ Generation Failed: {response['error']}")
            return False
            
        # Test 4: Query intent analysis
        print("\n4️⃣ Testing query intent analysis...")
        intent_response = llm_service.analyze_query_intent("Show me all the people in the database")
        
        if intent_response['success']:
            print(f"   ✅ Intent Analysis Success: True")
            print(f"   🎯 Query Type: {intent_response['analysis'].get('query_type', 'N/A')}")
            print(f"   🔍 Strategy: {intent_response['analysis'].get('recommended_strategy', 'N/A')}")
        else:
            print(f"   ❌ Intent Analysis Failed: {intent_response['error']}")
            
        # Test 5: System query generation
        print("\n5️⃣ Testing system query generation...")
        system_queries = llm_service.generate_system_queries(
            "Find documents about machine learning", 
            {"query_type": "semantic_similarity", "recommended_strategy": "hybrid_search"}
        )
        
        if system_queries['success']:
            print(f"   ✅ System Query Generation Success: True")
            solr_query = system_queries['system_queries'].get('solr_query', 'N/A')
            print(f"   🔍 Generated Solr Query: {solr_query[:100]}..." if len(solr_query) > 100 else f"   🔍 Generated Solr Query: {solr_query}")
        else:
            print(f"   ❌ System Query Generation Failed")
            
        print("\n🎉 All OLLAMA integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ollama_integration())
    if success:
        print("\n✅ OLLAMA Integration is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ OLLAMA Integration has issues that need to be fixed.")
        sys.exit(1)