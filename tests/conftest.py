"""
Shared test configuration and fixtures for NeoBoi platform tests
"""
import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add backend to Python path
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.config.settings import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings():
    """Provide application settings for tests."""
    return get_settings()


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


@pytest.fixture(scope="session")
def ollama_available():
    """Check if OLLAMA service is available."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


@pytest.fixture(scope="session")
def neo4j_available(settings):
    """Check if Neo4j service is available."""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        with driver.session() as session:
            result = session.run("RETURN 'test' as result")
            record = result.single()
            return record["result"] == "test"
    except:
        return False


@pytest.fixture(scope="session")
def solr_available(settings):
    """Check if Solr service is available."""
    try:
        import requests
        response = requests.get(f"{settings.solr_url}/solr/admin/info/system", timeout=2)
        return response.status_code == 200
    except:
        return False