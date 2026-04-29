import uuid
import json
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.column import BoardColumn, DEFAULT_COLUMNS
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.exceptions import NotFoundException, ForbiddenException
from app.services.notification_service import create_notification

def create_project(db: Session, project_in: ProjectCreate, current_user: User) -> Project:
    """Crea un proyecto, añade al creador como owner y genera las 4 columnas por defecto."""
    
    # 1. Crear el proyecto
    db_project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id
    )
    db.add(db_project)
    db.flush() # Para obtener el project.id
    
    # 2. Añadir al creador como owner en ProjectMember
    member = ProjectMember(
        project_id=db_project.id,
        user_id=current_user.id,
        role_in_project=ProjectMemberRole.owner
    )
    db.add(member)
    
    # 3. Crear las 4 columnas fijas
    for col_data in DEFAULT_COLUMNS:
        column = BoardColumn(
            project_id=db_project.id,
            name=col_data["name"],
            order=col_data["order"]
        )
        db.add(column)
        
    db.commit()
    db.refresh(db_project)
    return db_project

def get_user_projects(db: Session, current_user: User, skip: int = 0, limit: int = 20) -> tuple[List[Project], int]:
    """Obtiene los proyectos en los que el usuario es miembro (paginado)."""
    # Proyectos donde el usuario es miembro
    query = db.query(Project).join(ProjectMember).filter(ProjectMember.user_id == current_user.id)
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    return projects, total

def get_project_by_id(db: Session, project_id: uuid.UUID, current_user: User) -> Project:
    """Obtiene un proyecto si el usuario es miembro de este."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("Proyecto no encontrado.")
        
    # Verificar membresía
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise ForbiddenException("No eres miembro de este proyecto.")
        
    return project

def update_project(db: Session, project_id: uuid.UUID, project_in: ProjectUpdate, current_user: User) -> Project:
    """Actualiza un proyecto. Solo el owner o un profesor pueden hacerlo (regla de negocio simple)."""
    project = get_project_by_id(db, project_id, current_user)
    
    # Verificar si es owner (o profesor si quisiéramos esa lógica global, pero dejemos al owner por ahora)
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if member.role_in_project != ProjectMemberRole.owner and current_user.role.value != "professor":
        raise ForbiddenException("Solo el dueño del proyecto o un profesor pueden editarlo.")
        
    if project_in.name is not None:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description
        
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    return project

def delete_project(db: Session, project_id: uuid.UUID, current_user: User) -> None:
    """Elimina un proyecto. Solo el owner puede hacerlo."""
    project = get_project_by_id(db, project_id, current_user)
    
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if member.role_in_project != ProjectMemberRole.owner and current_user.role.value not in ["professor", "admin"]:
        raise ForbiddenException("Solo el dueño del proyecto, un profesor o un admin pueden eliminarlo.")
        
    db.delete(project)
    db.commit()

def add_project_feedback(db: Session, project_id: uuid.UUID, content: str, current_user: User) -> Project:
    """Añade una observación al array JSON de teacher_feedback."""
    project = get_project_by_id(db, project_id, current_user)
    
    if current_user.role.value not in ["professor", "admin"]:
        raise ForbiddenException("Solo profesores o administradores pueden añadir observaciones.")
        
    try:
        feedback_list = json.loads(project.teacher_feedback) if project.teacher_feedback else []
        if not isinstance(feedback_list, list): feedback_list = []
    except:
        feedback_list = []
        
    new_item = {
        "id": str(uuid.uuid4()),
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
        "resolved": False,
        "author_name": current_user.name
    }
    
    feedback_list.append(new_item)
    project.teacher_feedback = json.dumps(feedback_list)
    project.updated_at = datetime.utcnow()

    # ── Notificar a los estudiantes del proyecto ───────────────────────────
    student_members = (
        db.query(ProjectMember)
        .join(User, User.id == ProjectMember.user_id)
        .filter(
            ProjectMember.project_id == project_id,
            User.role == UserRole.student,
        )
        .all()
    )
    for member in student_members:
        create_notification(
            db=db,
            user_id=member.user_id,
            type="teacher_feedback",
            title="Nueva observación añadida",
            message=f"El profesor añadió una observación en el proyecto '{project.name}'.",
        )

    db.commit()
    db.refresh(project)
    return project

def delete_project_feedback(db: Session, project_id: uuid.UUID, feedback_id: str, current_user: User) -> Project:
    """Elimina una observación del array JSON."""
    project = get_project_by_id(db, project_id, current_user)
    
    if current_user.role.value not in ["professor", "admin"]:
        raise ForbiddenException("Solo profesores o administradores pueden eliminar observaciones.")
        
    try:
        feedback_list = json.loads(project.teacher_feedback) if project.teacher_feedback else []
        if not isinstance(feedback_list, list): feedback_list = []
    except:
        return project
        
    feedback_list = [item for item in feedback_list if item.get("id") != feedback_id]
    project.teacher_feedback = json.dumps(feedback_list)
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    return project

def resolve_project_feedback(db: Session, project_id: uuid.UUID, feedback_id: str, current_user: User) -> Project:
    """Marca una observación como resuelta en el array JSON."""
    project = get_project_by_id(db, project_id, current_user)
    
    if current_user.role.value not in ["professor", "admin"]:
        raise ForbiddenException("Solo profesores o administradores pueden resolver observaciones.")
        
    try:
        feedback_list = json.loads(project.teacher_feedback) if project.teacher_feedback else []
        if not isinstance(feedback_list, list): feedback_list = []
    except:
        return project
        
    for item in feedback_list:
        if item.get("id") == feedback_id:
            item["resolved"] = True
            break
            
    project.teacher_feedback = json.dumps(feedback_list)
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    return project
