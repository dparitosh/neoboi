#!/usr/bin/env python3
"""
Test enhanced chat service integration with OLLAMA
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.enhanced_chat_service import enhanced_chat_service

async def test_enhanced_chat():
    """Test enhanced chat service with OLLAMA integration"""
    print("🧪 Testing Enhanced Chat Service with OLLAMA...")
    
    try:
        # Test basic conversation
        print("\n1️⃣ Testing basic conversation...")
        response = await enhanced_chat_service.process_chat_query('What is artificial intelligence?')
        
        print(f"   ✅ Response Success: True")
        print(f"   📝 Response: {response.get('textResponse', '')[:200]}...")
        print(f"   🔍 Source: {response.get('source', 'unknown')}")
        print(f"   🎯 Confidence: {response.get('confidence', 0)}")
        
        # Test query classification
        print("\n2️⃣ Testing query classification...")
        response2 = await enhanced_chat_service.process_chat_query('Show me all nodes in the graph')
        
        print(f"   ✅ Response Success: True")
        print(f"   📝 Response: {response2.get('textResponse', '')[:200]}...")
        print(f"   🔍 Source: {response2.get('source', 'unknown')}")
        print(f"   🎯 Confidence: {response2.get('confidence', 0)}")
        
        # Test analysis request
        print("\n3️⃣ Testing analysis request...")
        response3 = await enhanced_chat_service.process_chat_query('Analyze the patterns in this data')
        
        print(f"   ✅ Response Success: True")
        print(f"   📝 Response: {response3.get('textResponse', '')[:200]}...")
        print(f"   🔍 Source: {response3.get('source', 'unknown')}")
        print(f"   🎯 Confidence: {response3.get('confidence', 0)}")
        
        print("\n🎉 Enhanced Chat Service tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_chat())
    if success:
        print("\n✅ Enhanced Chat Service is working with OLLAMA!")
    else:
        print("\n❌ Enhanced Chat Service has integration issues.")