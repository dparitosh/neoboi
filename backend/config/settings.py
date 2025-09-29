from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import List, Optional, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = PROJECT_ROOT / ".env.local"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env.local."""

    # Neo4j Configuration
    neo4j_uri: Optional[str] = Field(None, alias="NEO4J_URI")
    neo4j_user: Optional[str] = Field(None, alias="NEO4J_USER")
    neo4j_password: Optional[str] = Field(None, alias="NEO4J_PASSWORD")
    neo4j_database: Optional[str] = Field("neo4j", alias="NEO4J_DATABASE")

    # Solr Configuration
    solr_url: Optional[str] = Field("http://localhost:8983/solr", alias="SOLR_URL")
    solr_collection: Optional[str] = Field("neoboi_graph", alias="SOLR_COLLECTION")
    solr_home: Optional[str] = Field(None, alias="SOLR_HOME")
    solr_port: Optional[int] = Field(None, alias="SOLR_PORT")
    solr_bin_path: Optional[str] = Field(None, alias="SOLR_BIN_PATH")
    solr_start_command: Optional[str] = Field(None, alias="SOLR_START_COMMAND")
    solr_stop_command: Optional[str] = Field(None, alias="SOLR_STOP_COMMAND")
    solr_status_command: Optional[str] = Field(None, alias="SOLR_STATUS_COMMAND")

    # Server Configuration
    backend_protocol: Optional[str] = Field("http", alias="BACKEND_PROTOCOL")
    backend_host: Optional[str] = Field("127.0.0.1", alias="BACKEND_HOST")
    backend_port: Optional[int] = Field(8000, alias="BACKEND_PORT")
    backend_base_path: Optional[str] = Field("", alias="BACKEND_BASE_PATH")
    backend_url: Optional[str] = Field(None, alias="BACKEND_URL")
    frontend_host: Optional[str] = Field("127.0.0.1", alias="FRONTEND_HOST")
    frontend_port: Optional[int] = Field(3000, alias="FRONTEND_PORT")
    test_server_port: Optional[int] = Field(None, alias="TEST_SERVER_PORT")

    # CORS Configuration
    cors_allowed_origins: str = Field(
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000",
        alias="CORS_ALLOWED_ORIGINS",
    )

    # External Services
    ollama_host: Optional[str] = Field("http://localhost:11434", alias="OLLAMA_HOST")
    ollama_default_model: Optional[str] = Field("llama3", alias="OLLAMA_DEFAULT_MODEL")
    tika_server_url: Optional[str] = Field("http://localhost:9998", alias="TIKA_SERVER_URL")
    embedding_model: Optional[str] = Field("all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")

    # Application Settings
    log_level: Optional[str] = Field("INFO", alias="LOG_LEVEL")
    debug: Optional[bool] = Field(False, alias="DEBUG")
    environment: Optional[str] = Field("development", alias="ENVIRONMENT")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="allow",
    )

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """Parse CORS origins from string or list."""
        if not value:
            return "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"

        if isinstance(value, str):
            # Clean up the string but keep it as a string for storage
            return value.strip().strip('"')

        # Handle list input (convert back to string)
        if isinstance(value, list):
            return ",".join(str(origin).strip().strip('"\'' ) for origin in value if origin)

        return str(value)

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if not self.cors_allowed_origins:
            return []
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @field_validator("solr_url", "ollama_host", "tika_server_url", "backend_url", mode="before")
    @classmethod
    def strip_urls(cls, value: Optional[str]) -> Optional[str]:
        """Strip whitespace from URLs."""
        return value.strip() if isinstance(value, str) else value

    def model_post_init(self, __context: Any) -> None:
        """Set computed fields after initialization."""
        if not self.backend_url:
            base_path = self.backend_base_path or ""
            object.__setattr__(
                self,
                "backend_url",
                f"{self.backend_protocol}://{self.backend_host}:{self.backend_port}{base_path}",
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance of application settings."""
    return Settings()


def reload_settings() -> Settings:
    """Clear the cached settings and reload them from the environment."""
    get_settings.cache_clear()
    return get_settings()
