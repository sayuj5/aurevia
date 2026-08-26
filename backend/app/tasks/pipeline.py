import os
import asyncio
from celery import Celery
from backend.app.messaging.publisher import publish_event_sync
from backend.app.messaging.events import EventType
from backend.app.notifications.notification_service import dispatch_telegram_alert, create_in_app_notification

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("aurevia_tasks", broker=BROKER_URL, backend=BROKER_URL)

@celery_app.task(name="process_distress_pipeline")
def process_distress_pipeline(case_id: int, r_final: float, triage_level: str, reason: str):
    
    payload = {
        "event": EventType.TRIAGE_UPDATE,
        "case_id": case_id,
        "score": r_final,
        "triage_level": triage_level,
        "reason": reason
    }
    
    publish_event_sync("triage_events", payload)
    
    if triage_level == "CRITICAL" or r_final > 75.0:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.run_until_complete(dispatch_telegram_alert(case_id, r_final, triage_level, reason))
        loop.run_until_complete(create_in_app_notification(1, "Critical Distress Alert", f"Case {case_id} escalated", EventType.CRITICAL_ALERT))
        
    return {"status": "SUCCESS", "case_id": case_id}