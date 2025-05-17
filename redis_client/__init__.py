from settings import settings
import redis.asyncio as redis

def create_redis_client() -> redis.Redis:
    return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,)