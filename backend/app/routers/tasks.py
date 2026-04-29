import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskAssignmentBase, TaskAssignmentRead
from app.services.task_service import (
    create_task,
    get_tasks_by_project,
    get_task_by_id,
    update_task,
    delete_task,
    assign_user_to_task,
    remove_user_from_task
)

router = APIRouter(prefix="", tags=["Tasks"])

# --- Endpoints dependientes de Project ---
@router.post("/projects/{project_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create(project_id: uuid.UUID, task_in: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Crea una tarea dentro de un proyecto."""
    # Asegurar coherencia entre la URL y el body
    task_in.project_id = project_id
    return create_task(db, task_in, current_user)

@router.get("/projects/{project_id}/tasks", response_model=List[TaskRead])
def list_tasks_for_project(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtiene todas las tareas de un proyecto."""
    return get_tasks_by_project(db, project_id, current_user)


# --- Endpoints independientes de Task ---
@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtiene detalle de una tarea."""
    return get_task_by_id(db, task_id, current_user)

@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update(task_id: uuid.UUID, task_in: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Actualiza una tarea (útil para moverla de columna)."""
    return update_task(db, task_id, task_in, current_user)

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(task_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Elimina una tarea."""
    delete_task(db, task_id, current_user)
    return None


# --- Endpoints de asignación ---
@router.post("/tasks/{task_id}/assignments", response_model=TaskAssignmentRead, status_code=status.HTTP_201_CREATED)
def assign_user(task_id: uuid.UUID, assignment_in: TaskAssignmentBase, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Asigna un usuario a una tarea."""
    return assign_user_to_task(db, task_id, assignment_in, current_user)

@router.delete("/tasks/{task_id}/assignments/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(task_id: uuid.UUID, user_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remueve la asignación de un usuario a una tarea."""
    remove_user_from_task(db, task_id, user_id, current_user)
    return None
