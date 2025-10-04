"""
Cache Service for NeoBoi Application

Provides in-memory caching for search results and embeddings to improve performance.
Uses LRU (Least Recently Used) eviction policy with configurable TTL (Time To Live).

Features:
- LRU cache with size limits
- TTL-based expiration
- Cache hit/miss statistics
- Thread-safe operations
- Configurable cache sizes per operation type

Usage:
    from cache_service import CacheService

    cache = CacheService()
    cache_key = "search:solr:query=example&limit=20"

    # Try to get from cache
    result = cache.get(cache_key)
    if result is None:
        # Compute result
        result = expensive_operation()
        # Cache the result
        cache.set(cache_key, result, ttl_seconds=300)

    # Get cache statistics
    stats = cache.get_stats()
"""

import asyncio
import hashlib
import json
import logging
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class CacheEntry:
    """Represents a cache entry with value, timestamp, and TTL"""

    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.timestamp = time.time()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return time.time() - self.timestamp > self.ttl_seconds

    def get_age_seconds(self) -> float:
        """Get the age of the cache entry in seconds"""
        return time.time() - self.timestamp

class LRUCache:
    """Thread-safe LRU cache implementation"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if not entry.is_expired():
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    self.hits += 1
                    return entry.value
                else:
                    # Remove expired entry
                    del self.cache[key]
                    self.evictions += 1

            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set a value in the cache"""
        with self.lock:
            # Remove if already exists
            if key in self.cache:
                del self.cache[key]

            # Add new entry
            self.cache[key] = CacheEntry(value, ttl_seconds)

            # Evict if over capacity
            if len(self.cache) > self.max_size:
                # Remove least recently used (first item)
                evicted_key, _ = self.cache.popitem(last=False)
                self.evictions += 1
                logger.debug("Evicted cache key: %s", evicted_key)

    def delete(self, key: str) -> bool:
        """Delete a key from the cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_requests
            }

    def cleanup_expired(self) -> int:
        """Remove all expired entries, return count removed"""
        with self.lock:
            expired_keys = []
            for key, entry in self.cache.items():
                if entry.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                logger.debug("Cleaned up %d expired cache entries", len(expired_keys))

            return len(expired_keys)

class CacheService:
    """Main cache service with multiple cache instances for different types of data"""

    def __init__(self):
        # Separate caches for different types of data
        self.search_cache = LRUCache(max_size=500)  # Search results
        self.embedding_cache = LRUCache(max_size=200)  # Embeddings
        self.vector_cache = LRUCache(max_size=300)  # Vector search results
        self.integrated_cache = LRUCache(max_size=100)  # Integrated search results

        # Default TTL values (in seconds)
        self.default_ttl = {
            "search": 300,      # 5 minutes for search results
            "embedding": 3600,  # 1 hour for embeddings
            "vector": 600,      # 10 minutes for vector results
            "integrated": 300   # 5 minutes for integrated results
        }

        logger.info("Cache service initialized with separate caches for different data types")

    def _generate_cache_key(self, operation: str, params: Dict[str, Any]) -> str:
        """Generate a consistent cache key from operation and parameters"""
        # Sort parameters for consistent key generation
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        key_content = f"{operation}:{sorted_params}"

        # Use hash to keep key length reasonable
        key_hash = hashlib.md5(key_content.encode()).hexdigest()[:16]
        return f"{operation}:{key_hash}"

    def get_search_result(self, query: str, filters: Optional[Dict] = None, limit: int = 20) -> Optional[Any]:
        """Get cached search result"""
        params = {
            "query": query,
            "filters": filters or {},
            "limit": limit
        }
        cache_key = self._generate_cache_key("search", params)
        return self.search_cache.get(cache_key)

    def set_search_result(self, query: str, filters: Optional[Dict] = None, limit: int = 20,
                         result: Any = None, ttl_seconds: Optional[int] = None) -> None:
        """Cache search result"""
        params = {
            "query": query,
            "filters": filters or {},
            "limit": limit
        }
        cache_key = self._generate_cache_key("search", params)
        ttl = ttl_seconds or self.default_ttl["search"]
        self.search_cache.set(cache_key, result, ttl)

    def get_embedding(self, text: str) -> Optional[Any]:
        """Get cached embedding"""
        params = {"text": text}
        cache_key = self._generate_cache_key("embedding", params)
        return self.embedding_cache.get(cache_key)

    def set_embedding(self, text: str, embedding: Any, ttl_seconds: Optional[int] = None) -> None:
        """Cache embedding"""
        params = {"text": text}
        cache_key = self._generate_cache_key("embedding", params)
        ttl = ttl_seconds or self.default_ttl["embedding"]
        self.embedding_cache.set(cache_key, embedding, ttl)

    def get_vector_result(self, query: str, limit: int = 10) -> Optional[Any]:
        """Get cached vector search result"""
        params = {"query": query, "limit": limit}
        cache_key = self._generate_cache_key("vector", params)
        return self.vector_cache.get(cache_key)

    def set_vector_result(self, query: str, limit: int = 10, result: Any = None,
                         ttl_seconds: Optional[int] = None) -> None:
        """Cache vector search result"""
        params = {"query": query, "limit": limit}
        cache_key = self._generate_cache_key("vector", params)
        ttl = ttl_seconds or self.default_ttl["vector"]
        self.vector_cache.set(cache_key, result, ttl)

    def get_integrated_result(self, query: str, context: Optional[List] = None) -> Optional[Any]:
        """Get cached integrated search result"""
        params = {
            "query": query,
            "context": context or []
        }
        cache_key = self._generate_cache_key("integrated", params)
        return self.integrated_cache.get(cache_key)

    def set_integrated_result(self, query: str, context: Optional[List] = None,
                             result: Any = None, ttl_seconds: Optional[int] = None) -> None:
        """Cache integrated search result"""
        params = {
            "query": query,
            "context": context or []
        }
        cache_key = self._generate_cache_key("integrated", params)
        ttl = ttl_seconds or self.default_ttl["integrated"]
        self.integrated_cache.set(cache_key, result, ttl)

    def clear_all(self) -> None:
        """Clear all caches"""
        self.search_cache.clear()
        self.embedding_cache.clear()
        self.vector_cache.clear()
        self.integrated_cache.clear()
        logger.info("All caches cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            "search_cache": self.search_cache.get_stats(),
            "embedding_cache": self.embedding_cache.get_stats(),
            "vector_cache": self.vector_cache.get_stats(),
            "integrated_cache": self.integrated_cache.get_stats(),
            "overall": {
                "total_cached_items": (
                    len(self.search_cache.cache) +
                    len(self.embedding_cache.cache) +
                    len(self.vector_cache.cache) +
                    len(self.integrated_cache.cache)
                ),
                "total_hits": (
                    self.search_cache.hits +
                    self.embedding_cache.hits +
                    self.vector_cache.hits +
                    self.integrated_cache.hits
                ),
                "total_misses": (
                    self.search_cache.misses +
                    self.embedding_cache.misses +
                    self.vector_cache.misses +
                    self.integrated_cache.misses
                ),
                "total_evictions": (
                    self.search_cache.evictions +
                    self.embedding_cache.evictions +
                    self.vector_cache.evictions +
                    self.integrated_cache.evictions
                )
            }
        }

    async def cleanup_expired_async(self) -> Dict[str, int]:
        """Async cleanup of expired entries across all caches"""
        # Run cleanup in thread pool since it uses locks
        def cleanup_all():
            return {
                "search": self.search_cache.cleanup_expired(),
                "embedding": self.embedding_cache.cleanup_expired(),
                "vector": self.vector_cache.cleanup_expired(),
                "integrated": self.integrated_cache.cleanup_expired()
            }

        return await asyncio.get_event_loop().run_in_executor(None, cleanup_all)

# Global cache service instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get the global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service