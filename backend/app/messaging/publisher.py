import json
from backend.app.cache.redis_client import async_redis, sync_redis

async def publish_event_async(channel: str, message: dict):
    await async_redis.publish(channel, json.dumps(message))

def publish_event_sync(channel: str, message: dict):
    sync_redis.publish(channel, json.dumps(message))