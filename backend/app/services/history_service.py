import uuid
from typing import List, Optional, Any
from sqlalchemy.orm import Session, joinedload

from app.models.task_history import TaskHistory
from app.models.user import User
from app.models.column import BoardColumn

def log_task_change(
    db: Session, 
    task_id: uuid.UUID, 
    user_id: uuid.UUID, 
    field_name: str, 
    old_value: Any, 
    new_value: Any,
    commit: bool = False
) -> TaskHistory:
    """
    Registra un cambio en el historial de una tarea.
    Los valores se convierten a string para el registro general.
    """
    if old_value == new_value:
        return None # No hubo cambio real
        
    history_entry = TaskHistory(
        task_id=task_id,
        changed_by=user_id,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None
    )
    
    db.add(history_entry)
    
    # En muchos casos, este log es parte de otra transacción (ej. update_task).
    # Por eso commit es False por defecto, para comitear todo junto.
    if commit:
        db.commit()
        db.refresh(history_entry)
        
    return history_entry

def get_task_history(db: Session, task_id: uuid.UUID, current_user: User) -> List[TaskHistory]:
    """Obtiene el historial de cambios de una tarea con nombres legibles."""
    from app.services.task_service import get_task_by_id
    # Verificar acceso usando task_service
    task = get_task_by_id(db, task_id, current_user)
    
    # Cargar mapa de columnas del proyecto para resolver IDs → nombres
    columns = db.query(BoardColumn).filter(
        BoardColumn.project_id == task.project_id
    ).all()
    col_map = {str(c.id): c.name for c in columns}
    
    entries = db.query(TaskHistory).options(
        joinedload(TaskHistory.changed_by_user)
    ).filter(
        TaskHistory.task_id == task_id
    ).order_by(TaskHistory.changed_at.desc()).all()
    
    # Resolver column IDs a nombres legibles en los valores
    for entry in entries:
        if entry.field_name == "column_id":
            if entry.old_value and entry.old_value in col_map:
                entry.old_value = col_map[entry.old_value]
            if entry.new_value and entry.new_value in col_map:
                entry.new_value = col_map[entry.new_value]
    
    return entries
