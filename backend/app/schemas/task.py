import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.models.task import TaskPriority

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    project_id: uuid.UUID
    column_id: uuid.UUID

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    column_id: Optional[uuid.UUID] = None

class TaskAssignmentBase(BaseModel):
    user_id: uuid.UUID

class TaskAssignmentRead(TaskAssignmentBase):
    id: uuid.UUID
    task_id: uuid.UUID
    assigned_at: datetime
    assigned_by: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class TaskRead(TaskBase):
    id: uuid.UUID
    project_id: uuid.UUID
    column_id: uuid.UUID
    created_by: uuid.UUID
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    assignments: List[TaskAssignmentRead] = []

    model_config = ConfigDict(from_attributes=True)
