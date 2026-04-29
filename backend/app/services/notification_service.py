import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.core.exceptions import NotFoundException

def create_notification(
    db: Session,
    user_id: uuid.UUID,
    type: str,
    title: str,
    message: str,
    related_task_id: Optional[uuid.UUID] = None,
    commit: bool = False
) -> Notification:
    """Crea una nueva notificación para un usuario."""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        related_task_id=related_task_id
    )
    db.add(notification)
    
    if commit:
        db.commit()
        db.refresh(notification)
        
    return notification

def get_user_notifications(db: Session, current_user: User, unread_only: bool = False) -> List[Notification]:
    """Obtiene las notificaciones del usuario."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
        
    return query.order_by(Notification.created_at.desc()).all()

def mark_notification_as_read(db: Session, notification_id: uuid.UUID, current_user: User) -> Notification:
    """Marca una notificación específica como leída."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise NotFoundException("Notificación no encontrada.")
        
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification

def mark_all_as_read(db: Session, current_user: User) -> None:
    """Marca todas las notificaciones del usuario como leídas."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
