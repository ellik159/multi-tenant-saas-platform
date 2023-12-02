import redis
from src.core.config import settings

# Redis client for caching and rate limiting
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8"
)


def get_redis():
    """Dependency for getting Redis client"""
    return redis_client
