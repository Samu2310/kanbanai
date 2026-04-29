import uuid
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.models.task import Task, TaskAssignment
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskAssignmentBase
from app.services.project_service import get_project_by_id
from app.core.exceptions import NotFoundException, ConflictException
from app.services.history_service import log_task_change
from app.services.notification_service import create_notification

def create_task(db: Session, task_in: TaskCreate, current_user: User) -> Task:
    """Crea una nueva tarea en el proyecto y columna indicados."""
    # Verificar que el usuario tenga acceso al proyecto
    get_project_by_id(db, task_in.project_id, current_user)
    
    if current_user.role.value == "guest":
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Los invitados no pueden crear tareas.")

    db_task = Task(
        project_id=task_in.project_id,
        column_id=task_in.column_id,
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        due_date=task_in.due_date,
        created_by=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_project(db: Session, project_id: uuid.UUID, current_user: User) -> List[Task]:
    """Obtiene todas las tareas de un proyecto al que el usuario pertenece."""
    get_project_by_id(db, project_id, current_user)
    
    tasks = db.query(Task).options(
        joinedload(Task.creator)
    ).filter(Task.project_id == project_id).all()
    return tasks

def get_task_by_id(db: Session, task_id: uuid.UUID, current_user: User) -> Task:
    """Obtiene el detalle de una tarea."""
    task = db.query(Task).options(
        joinedload(Task.creator)
    ).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundException("Tarea no encontrada.")
        
    # Verificar acceso al proyecto de la tarea
    get_project_by_id(db, task.project_id, current_user)
    
    return task

def update_task(db: Session, task_id: uuid.UUID, task_in: TaskUpdate, current_user: User) -> Task:
    """Actualiza los datos de una tarea o la mueve de columna e intercepta los cambios."""
    task = get_task_by_id(db, task_id, current_user)
    
    # RBAC Control: solo guest bloqueado, student/professor/admin pueden editar cualquier tarea
    if current_user.role.value == "guest":
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Los invitados no pueden editar tareas.")
    
    # Rastrear cambios para el historial
    if task_in.title is not None and task_in.title != task.title:
        log_task_change(db, task.id, current_user.id, "title", task.title, task_in.title)
        task.title = task_in.title
        
    if task_in.description is not None and task_in.description != task.description:
        log_task_change(db, task.id, current_user.id, "description", task.description, task_in.description)
        task.description = task_in.description
        
    if task_in.priority is not None and task_in.priority != task.priority:
        log_task_change(db, task.id, current_user.id, "priority", task.priority.value, task_in.priority.value)
        task.priority = task_in.priority
        
    if task_in.due_date is not None and task_in.due_date != task.due_date:
        log_task_change(db, task.id, current_user.id, "due_date", task.due_date, task_in.due_date)
        task.due_date = task_in.due_date
        
    if task_in.column_id is not None and task_in.column_id != task.column_id:
        log_task_change(db, task.id, current_user.id, "column_id", task.column_id, task_in.column_id)
        task.column_id = task_in.column_id
        
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: uuid.UUID, current_user: User) -> None:
    """Elimina una tarea."""
    task = get_task_by_id(db, task_id, current_user)
    
    # RBAC Control: solo guest bloqueado, student/professor/admin pueden eliminar cualquier tarea
    from app.core.exceptions import ForbiddenException
    if current_user.role.value == "guest":
        raise ForbiddenException("Los invitados no pueden eliminar tareas.")
            
    db.delete(task)
    db.commit()

def assign_user_to_task(db: Session, task_id: uuid.UUID, assignment_in: TaskAssignmentBase, current_user: User) -> TaskAssignment:
    """Asigna un usuario a una tarea."""
    task = get_task_by_id(db, task_id, current_user)
    
    # Verificar que no esté asignado ya
    existing = db.query(TaskAssignment).filter(
        TaskAssignment.task_id == task_id,
        TaskAssignment.user_id == assignment_in.user_id
    ).first()
    
    if existing:
        raise ConflictException("El usuario ya está asignado a esta tarea.")
        
    assignment = TaskAssignment(
        task_id=task_id,
        user_id=assignment_in.user_id,
        assigned_by=current_user.id
    )
    db.add(assignment)
    
    log_task_change(db, task_id, current_user.id, "assignment", None, f"Assigned: {assignment_in.user_id}")
    
    # Crear notificación para el usuario asignado (si no se autoasigna)
    if assignment_in.user_id != current_user.id:
        create_notification(
            db=db,
            user_id=assignment_in.user_id,
            type="task_assigned",
            title="Nueva tarea asignada",
            message=f"Se te ha asignado a la tarea: {task.title}",
            related_task_id=task_id
        )
    
    db.commit()
    db.refresh(assignment)
    return assignment

def remove_user_from_task(db: Session, task_id: uuid.UUID, user_id: uuid.UUID, current_user: User) -> None:
    """Desasigna a un usuario de una tarea."""
    task = get_task_by_id(db, task_id, current_user) # Verificar acceso
    
    assignment = db.query(TaskAssignment).filter(
        TaskAssignment.task_id == task_id,
        TaskAssignment.user_id == user_id
    ).first()
    
    if not assignment:
        raise NotFoundException("El usuario no está asignado a esta tarea.")
        
    db.delete(assignment)
    
    log_task_change(db, task_id, current_user.id, "assignment", f"Unassigned: {user_id}", None)
    
    db.commit()
