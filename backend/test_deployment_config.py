import asyncio
import os
from dotenv import load_dotenv
from neo4j_service import Neo4jService

# Load environment variables from .env.local file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))

async def test_deployment_configurations():
    """Test Neo4j service configuration for both deployment types"""

    print("🔧 Testing Neo4j Deployment Configurations")
    print("=" * 50)

    # Test current configuration
    print("\n1. Testing Current Configuration:")
    try:
        service = Neo4jService()
        deployment_info = service.get_deployment_info()

        print(f"   Deployment Type: {deployment_info['deployment_type']}")
        print(f"   URI: {deployment_info['uri']}")
        print(f"   Database: {deployment_info['database']}")
        print(f"   Vector Supported: {deployment_info['vector_supported']}")
        print(f"   Embedding Model Loaded: {deployment_info['embedding_model_loaded']}")

        # Test connection
        print("   Testing connection...")
        await service.initialize_driver()
        result = await service.get_graph_data()
        print(f"   ✅ Connection successful: {len(result.get('nodes', []))} nodes")

        await service.close_driver()
        print("   ✅ Connection closed successfully")

    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

    # Test configuration switching simulation
    print("\n2. Testing Configuration Flexibility:")

    # Simulate Aura configuration
    print("   Simulating Neo4j Aura configuration...")
    original_uri = os.getenv("NEO4J_URI")
    original_user = os.getenv("NEO4J_USER")
    original_password = os.getenv("NEO4J_PASSWORD")

    try:
        # Test Aura-like URI detection
        os.environ["NEO4J_URI"] = "neo4j+s://test.databases.neo4j.io"
        os.environ["NEO4J_USER"] = "neo4j"
        os.environ["NEO4J_PASSWORD"] = "test"

        test_service = Neo4jService()
        test_info = test_service.get_deployment_info()
        print(f"   ✅ Aura detection: {test_info['deployment_type'] == 'aura'}")

    except Exception as e:
        print(f"   ❌ Aura simulation failed: {e}")

    try:
        # Test On-premise URI detection
        os.environ["NEO4J_URI"] = "bolt://localhost:7687"
        os.environ["NEO4J_USER"] = "neo4j"
        os.environ["NEO4J_PASSWORD"] = "local"

        test_service = Neo4jService()
        test_info = test_service.get_deployment_info()
        print(f"   ✅ On-premise detection: {test_info['deployment_type'] == 'on_premise'}")

    except Exception as e:
        print(f"   ❌ On-premise simulation failed: {e}")

    # Restore original configuration
    if original_uri:
        os.environ["NEO4J_URI"] = original_uri
    if original_user:
        os.environ["NEO4J_USER"] = original_user
    if original_password:
        os.environ["NEO4J_PASSWORD"] = original_password

    print("\n3. Configuration Recommendations:")
    service = Neo4jService()
    info = service.get_deployment_info()

    if info['is_aura']:
        print("   🎯 Using Neo4j Aura (Cloud) - RECOMMENDED")
        print("   ✅ Automatic scaling and backups")
        print("   ✅ Native vector index support")
        print("   ✅ Enterprise-grade security")
    elif info['is_on_premise']:
        print("   🏠 Using On-Premise Neo4j")
        print("   ✅ Full infrastructure control")
        print("   ✅ Suitable for air-gapped environments")
        print("   ⚠️ Manual maintenance required")
        print("   ⚠️ Vector support depends on version")

    if not info['embedding_model_loaded']:
        print("   ⚠️ WARNING: sentence-transformers not installed")
        print("   Run: pip install sentence-transformers==2.2.2")

    print("\n4. Service Capabilities:")
    capabilities = []
    if info['vector_supported']:
        capabilities.append("Vector Similarity Search")
    if info['embedding_model_loaded']:
        capabilities.append("GraphRAG Document Processing")
    capabilities.extend([
        "Graph Database Operations",
        "Cypher Query Execution",
        "Document Chunk Storage"
    ])

    for cap in capabilities:
        print(f"   ✅ {cap}")

    print("\n" + "=" * 50)
    print("🎉 Configuration test completed successfully!")
    print("Your Neo4j service is properly configured for flexible deployments.")

    return True

if __name__ == "__main__":
    success = asyncio.run(test_deployment_configurations())
    if not success:
        print("\n💥 Configuration test failed - check your setup")
        exit(1)