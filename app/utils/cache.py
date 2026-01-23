"""
Caching Utilities

This module provides simple in-memory caching for frequently accessed data.
For production use, consider using Redis or Memcached.
"""

import time
import threading
from functools import wraps
from typing import Any, Optional, Dict, Callable
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                return None

            item = self._cache[key]

            # Check if expired
            if time.time() > item['expires_at']:
                del self._cache[key]
                return None

            return item['value']

    def set(self, key: str, value: Any, timeout: int = 3600) -> None:
        """Set value in cache with TTL"""
        with self._lock:
            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + timeout
            }

    def delete(self, key: str) -> None:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """Clear all cache"""
        with self._lock:
            self._cache.clear()

    def cleanup(self) -> None:
        """Remove expired items from cache"""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, item in self._cache.items()
                if now > item['expires_at']
            ]
            for key in expired_keys:
                del self._cache[key]

    def get_or_set(self, key: str, factory: Callable, timeout: int = 3600) -> Any:
        """Get value from cache or set it using factory function"""
        value = self.get(key)
        if value is not None:
            return value

        value = factory()
        self.set(key, value, timeout)
        return value


# Global cache instance
_cache = SimpleCache()


def cache_result(timeout: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds (default: 1 hour)
        key_func: Function to generate cache key (receives function args)

    Usage:
        @cache_result(timeout=3600)
        def get_departments():
            return expensive_database_query()
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [f.__name__]
                key_parts.extend([str(arg) for arg in args])
                if kwargs:
                    sorted_kwargs = sorted(kwargs.items())
                    key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
                cache_key = ":".join(key_parts)

            # Try to get from cache
            result = _cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result

            # Cache miss, execute function
            result = f(*args, **kwargs)
            _cache.set(cache_key, result, timeout)
            logger.debug(f"Cache miss for {cache_key}, stored result")
            return result

        return decorated_function
    return decorator


def get_cache() -> SimpleCache:
    """Get the global cache instance"""
    return _cache


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate cache keys matching a pattern.

    Args:
        pattern: Pattern to match (simple string matching)

    Returns:
        int: Number of keys invalidated
    """
    with _cache._lock:
        keys_to_delete = [
            key for key in _cache._cache.keys()
            if pattern in key
        ]
        for key in keys_to_delete:
            del _cache._cache[key]
        return len(keys_to_delete)


# Predefined cache decorators for common data
cache_departments = cache_result(timeout=3600)  # 1 hour
cache_suppliers = cache_result(timeout=3600)  # 1 hour
cache_medicines = cache_result(timeout=1800)  # 30 minutes
cache_users = cache_result(timeout=1800)  # 30 minutes


def invalidate_all_cache():
    """Invalidate all cache (use with caution)"""
    _cache.clear()
    logger.info("All cache invalidated")


# Cache keys constants
CACHE_KEYS = {
    'departments': 'departments:all',
    'suppliers': 'suppliers:all',
    'medicines': 'medicines:all',
    'users': 'users:all',
    'stores': 'stores:all',
    'patient_count': 'stats:patient_count',
    'medicine_count': 'stats:medicine_count',
    'low_stock_medicines': 'stats:low_stock',
}


class CacheManager:
    """Manager for cache operations"""

    @staticmethod
    def get_departments():
        """Get cached departments"""
        return _cache.get(CACHE_KEYS['departments'])

    @staticmethod
    def set_departments(departments):
        """Set cached departments"""
        _cache.set(CACHE_KEYS['departments'], departments, 3600)

    @staticmethod
    def invalidate_departments():
        """Invalidate departments cache"""
        _cache.delete(CACHE_KEYS['departments'])

    @staticmethod
    def get_suppliers():
        """Get cached suppliers"""
        return _cache.get(CACHE_KEYS['suppliers'])

    @staticmethod
    def set_suppliers(suppliers):
        """Set cached suppliers"""
        _cache.set(CACHE_KEYS['suppliers'], suppliers, 3600)

    @staticmethod
    def invalidate_suppliers():
        """Invalidate suppliers cache"""
        _cache.delete(CACHE_KEYS['suppliers'])

    @staticmethod
    def get_medicines():
        """Get cached medicines"""
        return _cache.get(CACHE_KEYS['medicines'])

    @staticmethod
    def set_medicines(medicines):
        """Set cached medicines"""
        _cache.set(CACHE_KEYS['medicines'], medicines, 1800)

    @staticmethod
    def invalidate_medicines():
        """Invalidate medicines cache"""
        _cache.delete(CACHE_KEYS['medicines'])


# Export cache manager
cache_manager = CacheManager()
