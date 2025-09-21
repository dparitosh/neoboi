#!/usr/bin/env python3
"""
Test script for chat functionality with Ollama
"""
import asyncio

async def test_chat():
    try:
        from enhanced_chat_service import enhanced_chat_service

        print("Testing chat service with Ollama...")
        result = await enhanced_chat_service.process_chat_query('Hello, can you help me with graph analysis?')

        print("✅ Chat service is working!")
        print("Full response:")
        print(repr(result.get('textResponse', 'No response')))
        print(f"Response length: {len(result.get('textResponse', ''))}")
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Has graph data: {'graphData' in result}")

        # Debug LLM response
        if hasattr(enhanced_chat_service.llm_service, 'generate_response'):
            print("\nTesting direct LLM call...")
            direct_response = enhanced_chat_service.llm_service.generate_response("Say hello", max_tokens=50)
            print(f"Direct LLM response: {repr(direct_response.get('response', 'No response'))}")
            print(f"Direct LLM success: {direct_response.get('success', False)}")

        return True

    except Exception as e:
        print(f"❌ Chat service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_chat())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")