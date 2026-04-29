import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.schemas.column import ColumnRead
from app.models.project import ProjectMemberRole

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    teacher_feedback: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectFeedbackUpdate(BaseModel):
    feedback: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectMemberRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    role_in_project: ProjectMemberRole
    joined_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProjectRead(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProjectDetailRead(ProjectRead):
    """Lectura detallada que incluye columnas y miembros."""
    columns: List[ColumnRead] = []
    members: List[ProjectMemberRead] = []
