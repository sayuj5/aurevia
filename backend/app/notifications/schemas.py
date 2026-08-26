from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class NotificationSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    title: str
    message: str
    type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "UNREAD"