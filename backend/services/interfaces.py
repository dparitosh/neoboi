"""
Service Interfaces and Base Classes
This module defines interfaces and base classes to break circular dependencies
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol, Union
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    """Base configuration for all services"""
    host: str
    port: int
    timeout: int = 30


class LLMServiceProtocol(Protocol):
    """Protocol for LLM services"""

    async def generate_response(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response for the given prompt"""
        ...

    async def is_available(self) -> bool:
        """Check if the service is available"""
        ...


class VectorServiceProtocol(Protocol):
    """Protocol for vector/database services"""

    async def search_similar(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar content"""
        ...

    async def store_embedding(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content with its embedding"""
        ...

    def is_available(self) -> bool:
        """Check if the service is available"""
        ...


class ChatServiceProtocol(Protocol):
    """Protocol for chat services"""

    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chat message"""
        ...

    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history"""
        ...


class BaseService(ABC):
    """Base class for all services"""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self._initialized: bool = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Perform a health check"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources"""
        pass

    @property
    def is_initialized(self) -> bool:
        return self._initialized


# Service Registry for dependency injection
class ServiceRegistry:
    """Registry for service instances to avoid circular imports"""

    _instance: Optional['ServiceRegistry'] = None
    _services: Dict[str, Any] = {}

    def __new__(cls) -> 'ServiceRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str, service: Any) -> None:
        """Register a service instance"""
        cls._services[name] = service

    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        """Get a registered service instance"""
        return cls._services.get(name)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered services"""
        cls._services.clear()


# Lazy import helper
def lazy_import(module_path: str, class_name: str) -> Any:
    """Lazily import a class to avoid circular imports"""
    def _import() -> Any:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    return _import