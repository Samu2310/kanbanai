import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.notification import NotificationRead
from app.services.notification_service import (
    get_user_notifications,
    mark_notification_as_read,
    mark_all_as_read
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationRead])
def get_notifications(
    unread_only: bool = Query(False, description="Filtrar solo notificaciones no leídas"),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Obtiene las notificaciones del usuario autenticado."""
    return get_user_notifications(db, current_user, unread_only)

@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Marca una notificación como leída."""
    return mark_notification_as_read(db, notification_id, current_user)

@router.patch("/read-all", response_model=dict)
def mark_all_read(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Marca todas las notificaciones del usuario como leídas."""
    mark_all_as_read(db, current_user)
    return {"message": "Todas las notificaciones han sido marcadas como leídas."}
