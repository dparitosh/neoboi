"""
Unit tests for NeoBoi configuration system
"""
import pytest
from pathlib import Path
from backend.config.settings import Settings, get_settings


class TestSettings:
    """Test cases for application settings."""

    def test_settings_creation(self):
        """Test that settings can be created."""
        settings = get_settings()
        assert isinstance(settings, Settings)
        assert settings.neo4j_uri is not None
        assert settings.backend_port > 0

    def test_backend_url_construction(self, settings):
        """Test that backend URL is constructed correctly."""
        expected_url = f"{settings.backend_protocol}://{settings.backend_host}:{settings.backend_port}"
        assert settings.backend_url == expected_url

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from environment."""
        # Test comma-separated string
        origins_str = "http://localhost:3000,http://localhost:3001"
        origins = Settings.parse_cors_origins(origins_str)
        assert origins == ["http://localhost:3000", "http://localhost:3001"]

        # Test JSON array string
        origins_json = '["http://localhost:3000", "http://localhost:3001"]'
        origins = Settings.parse_cors_origins(origins_json)
        assert origins == ["http://localhost:3000", "http://localhost:3001"]

    def test_url_stripping(self):
        """Test that URLs are properly stripped of whitespace."""
        test_urls = [
            (" http://localhost:11434 ", "http://localhost:11434"),
            ("http://localhost:8983/solr ", "http://localhost:8983/solr"),
        ]

        for input_url, expected in test_urls:
            assert Settings.strip_urls(input_url) == expected

    @pytest.mark.unit
    def test_default_values(self, settings):
        """Test that default values are set correctly."""
        assert settings.backend_protocol == "http"
        assert settings.ollama_default_model == "llama3"
        assert settings.solr_collection == "neoboi_graph"
        assert settings.embedding_model == "all-MiniLM-L6-v2"