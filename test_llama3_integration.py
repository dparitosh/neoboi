#!/usr/bin/env python3
"""
LLAMA3 Integration Test for NeoBoi Platform
Tests the complete LLAMA3 integration with OLLAMA
"""
import asyncio
import json
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.unstructured_pipeline.llm_service import OfflineLLMService
from backend.enhanced_chat_service import EnhancedChatService

class LLAMA3IntegrationTester:
    """Comprehensive LLAMA3 integration testing"""
    
    def __init__(self):
        self.llm_service = OfflineLLMService()
        self.chat_service = EnhancedChatService()
        self.test_results = {}
        
    def test_ollama_connection(self):
        """Test basic OLLAMA connection"""
        print("🔍 Testing OLLAMA Connection...")
        
        try:
            is_available = self.llm_service.is_service_available()
            models = self.llm_service.list_available_models()
            
            self.test_results['ollama_connection'] = {
                'available': is_available,
                'models': models,
                'llama3_available': 'llama3' in models or 'llama3:latest' in models,
                'status': 'PASS' if is_available else 'FAIL'
            }
            
            print(f"   ✅ OLLAMA Available: {is_available}")
            print(f"   📊 Available Models: {models}")
            print(f"   🦙 LLAMA3 Available: {'llama3' in models or 'llama3:latest' in models}")
            
            return is_available and ('llama3' in models or 'llama3:latest' in models)
            
        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
            self.test_results['ollama_connection'] = {
                'available': False,
                'error': str(e),
                'status': 'FAIL'
            }
            return False
    
    def test_llama3_basic_generation(self):
        """Test basic LLAMA3 text generation"""
        print("\n🦙 Testing LLAMA3 Basic Generation...")
        
        try:
            test_prompt = "What is artificial intelligence? Explain in 2 sentences."
            
            response = self.llm_service.generate_response(
                prompt=test_prompt,
                model="llama3",
                max_tokens=100
            )
            
            self.test_results['llama3_generation'] = {
                'success': response.get('success', False),
                'model_used': response.get('model', 'unknown'),
                'response_length': len(response.get('response', '')),
                'has_response': bool(response.get('response', '').strip()),
                'status': 'PASS' if response.get('success') else 'FAIL'
            }
            
            if response.get('success'):
                print(f"   ✅ Generation Successful")
                print(f"   🎯 Model Used: {response.get('model')}")
                print(f"   📝 Response: {response.get('response', '')[:100]}...")
                print(f"   ⏱️  Duration: {response.get('total_duration', 0) / 1e9:.2f}s")
                return True
            else:
                print(f"   ❌ Generation Failed: {response.get('error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ Generation Error: {e}")
            self.test_results['llama3_generation'] = {
                'success': False,
                'error': str(e),
                'status': 'FAIL'
            }
            return False
    
    def test_llama3_advanced_capabilities(self):
        """Test LLAMA3 advanced capabilities"""
        print("\n🧠 Testing LLAMA3 Advanced Capabilities...")
        
        try:
            # Test document analysis
            test_document = """
            The Quick Brown Fox is a technology company founded in 2023 by John Smith and Alice Johnson.
            Located in San Francisco, California, the company specializes in artificial intelligence solutions
            for healthcare applications. Their flagship product, MedAI Pro, was launched in January 2024
            and has processed over 10,000 medical records to date.
            """
            
            analysis_result = self.llm_service.analyze_document(test_document, "business_report")
            
            # Test question answering
            qa_result = self.llm_service.answer_question(
                question="Who founded The Quick Brown Fox company?",
                context=test_document
            )
            
            # Test entity extraction
            entity_result = self.llm_service.extract_entities_llm(test_document)
            
            # Test classification
            classification_result = self.llm_service.classify_document(test_document)
            
            self.test_results['llama3_advanced'] = {
                'document_analysis': analysis_result.get('success', False),
                'question_answering': qa_result.get('success', False),
                'entity_extraction': entity_result.get('success', False),
                'classification': classification_result.get('success', False),
                'status': 'PASS' if all([
                    analysis_result.get('success'),
                    qa_result.get('success'),
                    entity_result.get('success'),
                    classification_result.get('success')
                ]) else 'PARTIAL'
            }
            
            print(f"   📊 Document Analysis: {'✅' if analysis_result.get('success') else '❌'}")
            print(f"   ❓ Question Answering: {'✅' if qa_result.get('success') else '❌'}")
            print(f"   🏷️  Entity Extraction: {'✅' if entity_result.get('success') else '❌'}")
            print(f"   📂 Classification: {'✅' if classification_result.get('success') else '❌'}")
            
            if qa_result.get('success'):
                print(f"   💡 QA Answer: {qa_result.get('qa_result', {}).get('answer', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Advanced Capabilities Error: {e}")
            self.test_results['llama3_advanced'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            return False
    
    async def test_enhanced_chat_integration(self):
        """Test LLAMA3 integration with Enhanced Chat Service"""
        print("\n💬 Testing Enhanced Chat Service with LLAMA3...")
        
        try:
            test_query = "What is artificial intelligence and how does it work?"
            conversation_id = f"test_{datetime.now().isoformat()}"
            
            # Process chat query using enhanced chat service
            response = await self.chat_service.process_chat_query(
                user_query=test_query,
                conversation_id=conversation_id
            )
            
            self.test_results['enhanced_chat_integration'] = {
                'success': bool(response.get('textResponse')),
                'has_graph_data': bool(response.get('graphData')),
                'confidence': response.get('confidence', 0),
                'source': response.get('source', 'unknown'),
                'conversation_context': bool(response.get('conversation_context')),
                'status': 'PASS' if response.get('textResponse') else 'FAIL'
            }
            
            print(f"   ✅ Chat Processing: {'Success' if response.get('textResponse') else 'Failed'}")
            print(f"   🎯 Response Source: {response.get('source', 'unknown')}")
            print(f"   📊 Confidence: {response.get('confidence', 0):.2f}")
            print(f"   💬 Response: {response.get('textResponse', 'N/A')[:100]}...")
            
            return bool(response.get('textResponse'))
            
        except Exception as e:
            print(f"   ❌ Enhanced Chat Integration Error: {e}")
            self.test_results['enhanced_chat_integration'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            return False
    
    def test_llama3_search_integration(self):
        """Test LLAMA3 integration with search capabilities"""
        print("\n🔍 Testing LLAMA3 Search Integration...")
        
        try:
            test_query = "Find information about artificial intelligence"
            
            # Test query intent analysis
            intent_analysis = self.llm_service.analyze_query_intent(test_query)
            
            # Test system queries generation
            system_queries = self.llm_service.generate_system_queries(
                test_query, 
                intent_analysis.get('analysis', {})
            )
            
            # Test search query generation
            search_query = self.llm_service.generate_search_query(test_query)
            
            self.test_results['llama3_search_integration'] = {
                'intent_analysis': intent_analysis.get('success', False),
                'system_queries': system_queries.get('success', False),
                'search_query_generation': search_query.get('success', False),
                'query_type': intent_analysis.get('analysis', {}).get('query_type', 'unknown'),
                'recommended_strategy': intent_analysis.get('analysis', {}).get('recommended_strategy', 'unknown'),
                'status': 'PASS' if all([
                    intent_analysis.get('success'),
                    system_queries.get('success'),
                    search_query.get('success')
                ]) else 'PARTIAL'
            }
            
            print(f"   🎯 Intent Analysis: {'✅' if intent_analysis.get('success') else '❌'}")
            print(f"   🔧 System Queries: {'✅' if system_queries.get('success') else '❌'}")
            print(f"   🔍 Search Query Gen: {'✅' if search_query.get('success') else '❌'}")
            
            if intent_analysis.get('success'):
                analysis = intent_analysis.get('analysis', {})
                print(f"   📊 Query Type: {analysis.get('query_type', 'unknown')}")
                print(f"   🎯 Strategy: {analysis.get('recommended_strategy', 'unknown')}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Search Integration Error: {e}")
            self.test_results['llama3_search_integration'] = {
                'error': str(e),
                'status': 'FAIL'
            }
            return False
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("🦙 LLAMA3 INTEGRATION TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') == 'PASS')
        partial_tests = sum(1 for result in self.test_results.values() 
                           if result.get('status') == 'PARTIAL')
        
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Partial: {partial_tests}")
        print(f"   Failed: {total_tests - passed_tests - partial_tests}")
        print(f"   Success Rate: {(passed_tests + partial_tests * 0.5) / total_tests * 100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = {
                'PASS': '✅',
                'PARTIAL': '🟡',
                'FAIL': '❌'
            }.get(result.get('status'), '❓')
            
            print(f"   {status_icon} {test_name.replace('_', ' ').title()}: {result.get('status')}")
            
            if result.get('error'):
                print(f"      Error: {result['error']}")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'partial': partial_tests,
                'failed': total_tests - passed_tests - partial_tests,
                'success_rate': (passed_tests + partial_tests * 0.5) / total_tests * 100
            },
            'results': self.test_results
        }
        
        with open('llama3_integration_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: llama3_integration_report.json")
        
        return report_data

async def main():
    """Run comprehensive LLAMA3 integration tests"""
    print("🚀 Starting LLAMA3 Integration Testing...")
    print("="*60)
    
    tester = LLAMA3IntegrationTester()
    
    # Run all tests
    tests_passed = []
    
    # Test 1: OLLAMA Connection
    tests_passed.append(tester.test_ollama_connection())
    
    # Only continue if OLLAMA is available
    if tests_passed[-1]:
        # Test 2: Basic Generation
        tests_passed.append(tester.test_llama3_basic_generation())
        
        # Test 3: Advanced Capabilities
        tests_passed.append(tester.test_llama3_advanced_capabilities())
        
        # Test 4: Enhanced Chat Integration
        tests_passed.append(await tester.test_enhanced_chat_integration())
        
        # Test 5: Search Integration
        tests_passed.append(tester.test_llama3_search_integration())
    
    # Generate comprehensive report
    report = tester.generate_report()
    
    print(f"\n🎯 Overall Result: {'SUCCESS' if all(tests_passed) else 'NEEDS ATTENTION'}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())