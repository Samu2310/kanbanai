import uuid
from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User

from sqlalchemy import String, Text, DateTime, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TaskHistory(Base):
    """
    Registro inmutable de cambios en una tarea (audit log).

    Cada vez que se modifica un campo relevante de Task, el servicio
    crea una entrada aquí con el valor anterior y el nuevo.

    Ejemplos de field_name:
        "column_id"    → la tarea se movió de columna
        "title"        → se renombró la tarea
        "priority"     → cambió la prioridad
        "due_date"     → cambió la fecha límite
        "description"  → se editó la descripción
        "assignment"   → se asignó o desasignó a un usuario
    """
    __tablename__ = "task_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    # Nombre del campo que cambió ("column_id", "title", "priority", etc.)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Los valores se almacenan como texto para máxima flexibilidad
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relaciones ────────────────────────────────────────────────────────────
    task: Mapped["Task"] = relationship("Task", back_populates="history")
    changed_by_user: Mapped["User"] = relationship(
        "User", back_populates="history_entries", foreign_keys=[changed_by]
    )

    @property
    def author_name(self) -> str:
        """Nombre del autor del cambio para serialización."""
        return self.changed_by_user.name if self.changed_by_user else "Desconocido"

    def __repr__(self) -> str:
        return (
            f"<TaskHistory task={self.task_id} "
            f"field={self.field_name!r} at={self.changed_at}>"
        )
