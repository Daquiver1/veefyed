"""Redis client for managing profile states and session data."""

import logging

from redis.exceptions import RedisError

import redis

app_logger = logging.getLogger("app")


class RedisClient:
    """Redis client."""

    def __init__(self, redis_url: str, timeout: int = 5) -> None:
        """Initialize Redis client."""
        self.redis_url = redis_url
        self.timeout = timeout
        self._redis: redis.StrictRedis | None = None

    @property
    def redis(self) -> redis.StrictRedis:
        """Lazy load the Redis connection."""
        if self._redis is None:
            self._redis = redis.StrictRedis.from_url(
                self.redis_url, socket_timeout=self.timeout, decode_responses=True
            )
        assert self._redis is not None
        return self._redis

    def clear_everything(self) -> None:
        """Clear ALL data in the current Redis database."""
        try:
            self.redis.flushdb()
            app_logger.info("All Redis data cleared.")
        except RedisError as e:
            app_logger.info(f"Redis error: {e}")

    def get_cache(self, *, key: str, repo_name: str) -> str | None:
        """Get a cached value."""
        try:
            cache_key = f"cache:{repo_name}:{key}"
            cached_value = self.redis.get(cache_key)
            return cached_value if cached_value else None
        except RedisError as e:
            app_logger.info(f"Redis error getting cache {key}: {e}")
            return None

    def set_cache(
        self, *, repo_name: str, key: str, value: str, ttl: int = 3600
    ) -> bool:
        """Cache a value with TTL (default 1 hour)."""
        try:
            cache_key = f"cache:{repo_name}:{key}"
            return self.redis.setex(cache_key, ttl, value)
        except RedisError as e:
            app_logger.info(f"Redis error setting cache {key}: {e}")
            return False

    def invalidate_cache(self, *, repo_name: str, key: str) -> bool:
        """Invalidate a cached value."""
        try:
            cache_key = f"cache:{repo_name}:{key}"
            return self.redis.delete(cache_key) > 0
        except RedisError as e:
            app_logger.info(f"Redis error invalidating cache {key}: {e}")
            return False

    def invalidate_repo_cache(self, repo_name: str) -> bool:
        """Invalidate all cached values."""
        try:
            pattern = f"cache:{repo_name}:*"
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys) > 0
            return True
        except RedisError as e:
            app_logger.info(f"Redis error invalidating all cache: {e}")
            return False
