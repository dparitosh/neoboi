#!/usr/bin/env python3
"""
Test script for chat functionality with Ollama
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_chat():
    try:
        from backend.enhanced_chat_service import enhanced_chat_service

        print("Testing chat service with Ollama...")
        result = await enhanced_chat_service.process_chat_query('Hello, can you help me with graph analysis?')

        print("✅ Chat service is working!")
        print("Full response:")
        print(result.get('textResponse', 'No response'))
        print(f"Source: {result.get('source', 'unknown')}")
        print(f"Has graph data: {'graphData' in result}")

        return True

    except Exception as e:
        print(f"❌ Chat service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_chat())
    sys.exit(0 if success else 1)