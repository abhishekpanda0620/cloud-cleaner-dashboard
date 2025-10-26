"""Caching utility for AWS API responses"""
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
import logging
from functools import wraps
import hashlib
import json

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._default_ttl = timedelta(minutes=5)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.now() < expiry:
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                logger.debug(f"Cache expired for key: {key}")
                del self._cache[key]
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self._default_ttl
        expiry = datetime.now() + ttl
        self._cache[key] = (value, expiry)
        logger.debug(f"Cache set for key: {key}, expires at: {expiry}")
    
    def delete(self, key: str) -> None:
        """Delete specific key from cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching pattern"""
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            del self._cache[key]
        logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")
    
    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self._cache)
        expired_entries = sum(1 for _, expiry in self._cache.values() if datetime.now() >= expiry)
        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries
        }


# Global cache instance
_cache = SimpleCache()


def get_cache() -> SimpleCache:
    """Get the global cache instance"""
    return _cache


def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments"""
    # Create a string representation of args and kwargs
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    # Hash it to create a shorter key
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl_minutes: int = 5, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl_minutes: Time to live in minutes
        key_prefix: Prefix for cache key (useful for invalidation)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = _cache.get(func_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            _cache.set(func_key, result, timedelta(minutes=ttl_minutes))
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = _cache.get(func_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            _cache.set(func_key, result, timedelta(minutes=ttl_minutes))
            return result
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def invalidate_cache(pattern: str) -> None:
    """Invalidate cache entries matching pattern"""
    _cache.invalidate_pattern(pattern)


def clear_cache() -> None:
    """Clear all cache"""


def get_redis_client():
    """Get Redis client for direct Redis operations"""
    import redis
    from core.config import settings
    
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        decode_responses=False
    )
    _cache.clear()