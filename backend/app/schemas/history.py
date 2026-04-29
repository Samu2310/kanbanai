import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TaskHistoryRead(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    changed_by: uuid.UUID
    author_name: Optional[str] = None
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
