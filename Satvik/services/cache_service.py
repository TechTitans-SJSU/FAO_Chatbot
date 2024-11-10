# services/cache_service.py
import redis
import json
from typing import Optional
import os

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
        self.expiration_time = 3600  # Cache for 1 hour

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            return self.redis_client.get(key)
        except redis.RedisError:
            return None

    async def set(self, key: str, value: str):
        """Set value in cache"""
        try:
            self.redis_client.setex(
                name=key,
                time=self.expiration_time,
                value=value
            )
        except redis.RedisError:
            pass  # Fail silently, just don't cache

    async def clear(self):
        """Clear all cached data"""
        try:
            self.redis_client.flushdb()
        except redis.RedisError:
            pass