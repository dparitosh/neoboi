#!/usr/bin/env python3
"""
Test script for Ollama offline LLM integration
"""
import sys
import os
import asyncio
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from unstructured_pipeline.llm_service import OfflineLLMService

async def test_ollama_integration():
    """Test Ollama integration with comprehensive checks"""
    print("=== Ollama Integration Test ===\n")

    # Initialize service
    llm_service = OfflineLLMService()

    # Test 1: Service availability
    print("1. Testing service availability...")
    is_available = llm_service.is_service_available()
    print(f"   Service available: {'✓' if is_available else '✗'}")

    if not is_available:
        print("   ❌ Ollama service is not running!")
        print("   Please start Ollama with: ollama serve")
        return False

    # Test 2: List available models
    print("\n2. Testing model listing...")
    models = llm_service.list_available_models()
    print(f"   Available models: {len(models)} found")
    for model in models[:5]:  # Show first 5
        print(f"   - {model}")
    if len(models) > 5:
        print(f"   ... and {len(models) - 5} more")

    if not models:
        print("   ❌ No models available!")
        print("   Install a model with: ollama pull llama2:7b")
        return False

    # Test 3: Basic text generation
    print("\n3. Testing basic text generation...")
    try:
        response = llm_service.generate_response(
            "Say hello and introduce yourself in one sentence.",
            max_tokens=100
        )
        if response['success']:
            print("   ✓ Generation successful")
            print(f"   Response: {response['response'][:100]}...")
            print(f"   Model: {response['model']}")
            print(f"   Processing time: {response.get('total_duration', 0) / 1e9:.2f}s")
        else:
            print(f"   ❌ Generation failed: {response['error']}")
            return False
    except Exception as e:
        print(f"   ❌ Generation error: {str(e)}")
        return False

    # Test 4: Document analysis
    print("\n4. Testing document analysis...")
    test_document = """
    Artificial Intelligence (AI) is revolutionizing various industries.
    Machine learning algorithms can process vast amounts of data to make predictions.
    Natural language processing helps computers understand human language.
    Computer vision enables machines to interpret visual information.
    """

    try:
        analysis = llm_service.analyze_document(test_document, "text")
        if analysis['success']:
            print("   ✓ Document analysis successful")
            analysis_data = analysis.get('analysis', {})
            if isinstance(analysis_data, dict):
                print(f"   Summary: {analysis_data.get('summary', 'N/A')[:100]}...")
                print(f"   Topics: {analysis_data.get('topics', [])}")
            print(f"   Processing time: {analysis.get('processing_time', 0):.2f}s")
        else:
            print(f"   ❌ Analysis failed: {analysis['error']}")
            return False
    except Exception as e:
        print(f"   ❌ Analysis error: {str(e)}")
        return False

    # Test 5: Question answering
    print("\n5. Testing question answering...")
    try:
        qa_result = llm_service.answer_question(
            "What is artificial intelligence?",
            test_document
        )
        if qa_result['success']:
            print("   ✓ Q&A successful")
            qa_data = qa_result.get('qa_result', {})
            if isinstance(qa_data, dict):
                print(f"   Answer: {qa_data.get('answer', 'N/A')[:100]}...")
                print(f"   Confidence: {qa_data.get('confidence', 'N/A')}")
            print(f"   Processing time: {qa_result.get('processing_time', 0):.2f}s")
        else:
            print(f"   ❌ Q&A failed: {qa_result['error']}")
            return False
    except Exception as e:
        print(f"   ❌ Q&A error: {str(e)}")
        return False

    # Test 6: Entity extraction
    print("\n6. Testing entity extraction...")
    try:
        entities = llm_service.extract_entities_llm(test_document)
        if entities['success']:
            print("   ✓ Entity extraction successful")
            entity_data = entities.get('entities', {})
            if isinstance(entity_data, dict):
                for entity_type, entity_list in entity_data.items():
                    if isinstance(entity_list, list) and entity_list:
                        print(f"   {entity_type}: {entity_list[:3]}")  # Show first 3
            print(f"   Model: {entities['model']}")
        else:
            print(f"   ❌ Entity extraction failed: {entities['error']}")
            return False
    except Exception as e:
        print(f"   ❌ Entity extraction error: {str(e)}")
        return False

    # Test 7: Search query generation
    print("\n7. Testing search query enhancement...")
    try:
        search_query = llm_service.generate_search_query("find documents about AI technology")
        if search_query['success']:
            print("   ✓ Search query generation successful")
            search_data = search_query.get('search_params', {})
            if isinstance(search_data, dict):
                print(f"   Keywords: {search_data.get('keywords', 'N/A')}")
                print(f"   Entity types: {search_data.get('entity_types', [])}")
            print(f"   Original query: {search_query['original_query']}")
        else:
            print(f"   ❌ Search query generation failed: {search_query['error']}")
            return False
    except Exception as e:
        print(f"   ❌ Search query error: {str(e)}")
        return False

    # Success summary
    print("\n" + "="*50)
    print("🎉 ALL TESTS PASSED!")
    print("Ollama integration is working correctly.")
    print("="*50)

    # Performance summary
    print("\n📊 Performance Summary:")
    print(f"   Service: {'Available' if is_available else 'Unavailable'}")
    print(f"   Models: {len(models)} available")
    print(f"   Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return True

async def main():
    """Main test function"""
    try:
        success = await test_ollama_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())