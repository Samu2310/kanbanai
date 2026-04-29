import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Notification(Base):
    """
    Notificación interna del sistema para un usuario.

    Tipos comunes de notificación (campo 'type'):
        "task_assigned"   → te asignaron una tarea
        "task_due_soon"   → una tarea tuya vence pronto
        "task_overdue"    → una tarea está vencida
        "task_moved"      → una tarea fue movida de columna
        "ai_alert"        → la IA detectó un riesgo o patrón relevante
        "project_invite"  → te invitaron a un proyecto
    """
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Tarea relacionada (opcional — algunas notificaciones no son de tareas)
    related_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )
    # Token de invitación (solo para notificaciones type="project_invite")
    invitation_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relaciones ────────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(
        "User", back_populates="notifications", foreign_keys=[user_id]
    )
    related_task: Mapped[Optional["Task"]] = relationship(
        "Task", back_populates="notifications", foreign_keys=[related_task_id]
    )

    def __repr__(self) -> str:
        return (
            f"<Notification user={self.user_id} "
            f"type={self.type!r} read={self.is_read}>"
        )
