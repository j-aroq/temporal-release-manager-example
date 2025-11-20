"""
Simple in-memory cache with TTL support.

Provides caching functionality for frequently accessed data with automatic expiration.
In production, consider replacing with Redis or Memcached.
"""

import time
from typing import Any, Dict, Optional, Tuple
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class TTLCache:
    """
    Time-To-Live cache implementation.

    Stores values with expiration times and automatically removes stale entries.
    Thread-safe for concurrent access.
    """

    def __init__(self, default_ttl: int = 10):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expiry = self._cache[key]

            # Check if expired
            if time.time() > expiry:
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache miss (expired): {key}")
                return None

            self._hits += 1
            logger.debug(f"Cache hit: {key}")
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)

        with self._lock:
            self._cache[key] = (value, expiry)
            logger.debug(f"Cache set: {key} (TTL: {ttl or self.default_ttl}s)")

    def delete(self, key: str) -> None:
        """
        Remove value from cache.

        Args:
            key: Cache key
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache delete: {key}")

    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache cleared ({count} entries)")

    def cleanup(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []

        with self._lock:
            for key, (_, expiry) in self._cache.items():
                if current_time > expiry:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

        if expired_keys:
            logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")

        return len(expired_keys)

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.1f}%",
            }


# Global cache instance for release list
_release_cache: Optional[TTLCache] = None


def get_release_cache() -> TTLCache:
    """Get or create global release cache instance."""
    global _release_cache
    if _release_cache is None:
        _release_cache = TTLCache(default_ttl=10)  # 10 second TTL
    return _release_cache
