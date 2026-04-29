import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class NotificationRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str
    message: str
    is_read: bool
    related_task_id: Optional[uuid.UUID] = None
    invitation_token: Optional[str] = None   # Token para invitaciones
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
