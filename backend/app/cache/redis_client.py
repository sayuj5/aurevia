import os
import redis.asyncio as aioredis
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

async_redis = aioredis.from_url(REDIS_URL, decode_responses=True)
sync_redis = redis.from_url(REDIS_URL, decode_responses=True)