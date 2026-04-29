import uuid
from pydantic import BaseModel, ConfigDict

class ColumnRead(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    order: int
    
    model_config = ConfigDict(from_attributes=True)
