import os
import httpx
import json
from backend.app.cache.redis_client import async_redis
from backend.app.notifications.schemas import NotificationSchema
from backend.app.messaging.publisher import publish_event_async
from backend.app.messaging.events import EventType

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

async def create_in_app_notification(user_id: int, title: str, message: str, event_type: str = EventType.NOTIFICATION):
    notif = NotificationSchema(user_id=user_id, title=title, message=message, type=event_type)
    payload = notif.model_dump_json()
    
    await async_redis.hset(f"notifications:{user_id}", notif.id, payload)
    await publish_event_async("triage_events", {"event": EventType.NOTIFICATION, "data": json.loads(payload)})

async def dispatch_telegram_alert(case_id: int, score: float, triage_level: str, reason: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
        
    text = (
        f"🚨 *AUREVIA CRITICAL ESCALATION*\n"
        f"*Case ID:* {case_id}\n"
        f"*Score:* {score}/100\n"
        f"*Tier:* {triage_level}\n"
        f"*Trigger:* {reason}\n"
        f"*Action:* Immediate Intervention Required"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"})
            return res.status_code == 200
    except Exception:
        return False