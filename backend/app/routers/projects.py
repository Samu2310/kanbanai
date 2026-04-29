import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.utils.pagination import PaginationParams, PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectDetailRead, ProjectFeedbackUpdate
from app.services.project_service import (
    create_project,
    get_user_projects,
    get_project_by_id,
    update_project,
    delete_project,
    add_project_feedback,
    delete_project_feedback,
    resolve_project_feedback
)
from app.services.invitation_service import send_invitation_by_email
from app.schemas.invitation import InviteSendRequest, InviteSendResponse

router = APIRouter(prefix="/projects", tags=["Projects"], redirect_slashes=True)

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create(project_in: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Crea un nuevo proyecto. Genera automáticamente las 4 columnas del Kanban."""
    return create_project(db, project_in, current_user)

@router.get("", response_model=PaginatedResponse[ProjectRead])
def list_projects(params: PaginationParams = Depends(), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lista los proyectos en los que el usuario es miembro."""
    projects, total = get_user_projects(db, current_user, skip=params.offset, limit=params.page_size)
    return PaginatedResponse.build(items=projects, total=total, page=params.page, page_size=params.page_size)

@router.get("/{project_id}", response_model=ProjectDetailRead)
def get_project(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtiene el detalle de un proyecto, incluyendo sus columnas y miembros."""
    return get_project_by_id(db, project_id, current_user)

@router.patch("/{project_id}", response_model=ProjectRead)
def update(project_id: uuid.UUID, project_in: ProjectUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Actualiza la información básica de un proyecto."""
    return update_project(db, project_id, project_in, current_user)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Elimina un proyecto y todas sus dependencias (columnas, tareas)."""
    delete_project(db, project_id, current_user)
    return None

@router.post("/{project_id}/invitations", response_model=InviteSendResponse, status_code=status.HTTP_201_CREATED)
def send_project_invitation(
    project_id: uuid.UUID,
    request: InviteSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Envía una invitación a otro usuario por email para este proyecto."""
    print(f"DEBUG: Enviando invitación para proyecto {project_id} a {request.email}")
    return send_invitation_by_email(db, project_id, request.email, current_user)

@router.get("/{project_id}/feedback", response_model=dict)
def get_feedback(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtiene el feedback del profesor para este proyecto."""
    project = get_project_by_id(db, project_id, current_user)
    try:
        import json
        items = json.loads(project.teacher_feedback) if project.teacher_feedback else []
    except:
        items = []
    return {"feedback": items}

@router.post("/{project_id}/feedback", response_model=ProjectRead)
def add_feedback(project_id: uuid.UUID, update_data: ProjectFeedbackUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Añade una nueva observación."""
    return add_project_feedback(db, project_id, update_data.feedback, current_user)

@router.delete("/{project_id}/feedback/{feedback_id}", response_model=ProjectRead)
def delete_feedback(project_id: uuid.UUID, feedback_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Elimina una observación."""
    return delete_project_feedback(db, project_id, feedback_id, current_user)

@router.patch("/{project_id}/feedback/{feedback_id}/resolve", response_model=ProjectRead)
def resolve_feedback(project_id: uuid.UUID, feedback_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Marca una observación como resuelta."""
    return resolve_project_feedback(db, project_id, feedback_id, current_user)
