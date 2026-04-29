import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.history import TaskHistoryRead
from app.services.history_service import get_task_history

router = APIRouter(prefix="/tasks/{task_id}/history", tags=["History"])

@router.get("", response_model=List[TaskHistoryRead])
def get_history(task_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtiene el historial de cambios de una tarea.
    Los registros se ordenan del más reciente al más antiguo.
    """
    return get_task_history(db, task_id, current_user)
