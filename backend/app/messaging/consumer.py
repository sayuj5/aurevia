import asyncio
import json
from backend.app.cache.redis_client import async_redis

async def listen_to_channel(channel: str, callback_function):
    pubsub = async_redis.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = json.loads(message["data"])
                await callback_function(data)
            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        await pubsub.unsubscribe(channel)