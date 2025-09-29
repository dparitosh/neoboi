# Neo4j GraphRAG with OLLAMA Integration Example
"""
This example shows how to use neo4j_graphrag with OLLAMA instead of OpenAI.
The neo4j_graphrag library supports OLLAMA through the OllamaLLM class.
"""

from neo4j_graphrag.llm import OllamaLLM
from neo4j_graphrag.retrievers import ToolsRetriever, VectorRetriever
import neo4j

# Your existing OLLAMA configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3"  # or your preferred model

# Neo4j connection (same as your current setup)
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "tcs#12345"

def create_ollama_llm():
    """Create OLLAMA LLM instance for neo4j_graphrag"""
    return OllamaLLM(
        model_name=OLLAMA_MODEL,
        model_params={
            "base_url": OLLAMA_HOST,
            "temperature": 0.7,
            "num_predict": 500,
        }
    )

def create_neo4j_driver():
    """Create Neo4j driver instance"""
    return neo4j.GraphDatabase.driver(
        NEO4J_URI,
        auth=neo4j.basic_auth(NEO4J_USER, NEO4J_PASSWORD)
    )

# Example 1: Basic ToolsRetriever with OLLAMA
def example_tools_retriever():
    """Example using ToolsRetriever with OLLAMA LLM"""

    # Create OLLAMA LLM (replaces OpenAILLM)
    llm = create_ollama_llm()
    driver = create_neo4j_driver()

    # Create a simple tool for demonstration
    from neo4j_graphrag.retrievers.external import Tool

    class DocumentSearchTool(Tool):
        """Simple document search tool"""
        name = "document_search"
        description = "Search for documents in the knowledge graph"

        def run(self, query: str) -> str:
            # Your existing search logic here
            return f"Found documents related to: {query}"

    # Create ToolsRetriever with OLLAMA
    tools_retriever = ToolsRetriever(
        driver=driver,
        llm=llm,
        tools=[DocumentSearchTool()],
        neo4j_database="neo4j"
    )

    # Perform a search
    result = tools_retriever.search("Tell me about machine learning")
    print("ToolsRetriever Result:", result)

# Example 2: VectorRetriever with OLLAMA (if you have vector embeddings)
def example_vector_retriever():
    """Example using VectorRetriever with OLLAMA LLM"""

    llm = create_ollama_llm()
    driver = create_neo4j_driver()

    # Vector retriever for semantic search
    vector_retriever = VectorRetriever(
        driver=driver,
        llm=llm,
        index_name="document_chunks_vector",  # Your vector index name
        neo4j_database="neo4j"
    )

    # Search with semantic understanding
    result = vector_retriever.search("Find documents about AI")
    print("VectorRetriever Result:", result)

# Example 3: Integrating with your existing system
def integrate_with_existing_system():
    """
    How to integrate neo4j_graphrag with your existing NeoBoi system
    """

    # Your existing services
    from backend.neo4j_service import Neo4jService
    from backend.unstructured_pipeline.llm_service import OfflineLLMService

    # Create neo4j_graphrag compatible LLM
    ollama_llm = create_ollama_llm()

    # Your existing Neo4j service
    neo4j_service = Neo4jService()
    driver = neo4j_service.get_driver()

    # Create retrievers using neo4j_graphrag
    tools_retriever = ToolsRetriever(
        driver=driver,
        llm=ollama_llm,
        tools=[],  # Add your custom tools here
        neo4j_database=neo4j_service.database
    )

    # Use in your existing search methods
    def enhanced_integrated_search(query: str):
        """Enhanced search combining your existing logic with neo4j_graphrag"""

        # Your existing integrated search
        existing_results = neo4j_service.integrated_search(query)

        # Add neo4j_graphrag powered retrieval
        graphrag_results = tools_retriever.search(query)

        # Combine results
        combined = {
            "query": query,
            "existing_results": existing_results,
            "graphrag_results": graphrag_results,
            "combined_insights": "Integrated analysis from both systems"
        }

        return combined

    return enhanced_integrated_search

if __name__ == "__main__":
    print("Neo4j GraphRAG with OLLAMA Examples")
    print("=" * 50)

    # Test basic functionality
    try:
        llm = create_ollama_llm()
        driver = create_neo4j_driver()

        print("✅ OLLAMA LLM created successfully")
        print("✅ Neo4j driver created successfully")

        # Test LLM connectivity
        test_response = llm.invoke("Hello, test message")
        print(f"✅ LLM test response: {test_response.content[:100]}...")

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Make sure OLLAMA is running and Neo4j is accessible")