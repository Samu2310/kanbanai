import uuid
import enum
from datetime import datetime, date
from typing import Optional, List
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.column import BoardColumn
    from app.models.user import User
    from app.models.task_history import TaskHistory
    from app.models.notification import Notification

from sqlalchemy import String, Text, DateTime, Date, ForeignKey, Enum as SAEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TaskPriority(str, enum.Enum):
    """Nivel de prioridad de una tarea."""
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("columns.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, name="taskpriority"),
        nullable=False,
        default=TaskPriority.medium,
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relaciones ────────────────────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    column: Mapped["BoardColumn"] = relationship("BoardColumn", back_populates="tasks")
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_tasks", foreign_keys=[created_by]
    )
    assignments: Mapped[List["TaskAssignment"]] = relationship(
        "TaskAssignment", back_populates="task", cascade="all, delete-orphan"
    )
    history: Mapped[List["TaskHistory"]] = relationship(
        "TaskHistory", back_populates="task", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="related_task"
    )

    @property
    def created_by_name(self) -> str:
        """Nombre del creador para serialización."""
        return self.creator.name if self.creator else "Desconocido"

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} priority={self.priority}>"


class TaskAssignment(Base):
    """Relación muchos-a-muchos entre tareas y usuarios asignados."""
    __tablename__ = "task_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Quién realizó la asignación (puede ser diferente al asignado)
    assigned_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # ─── Relaciones ────────────────────────────────────────────────────────────
    task: Mapped["Task"] = relationship("Task", back_populates="assignments")
    user: Mapped["User"] = relationship(
        "User", back_populates="task_assignments", foreign_keys=[user_id]
    )
    assigner: Mapped["User"] = relationship(
        "User", foreign_keys=[assigned_by]
    )

    def __repr__(self) -> str:
        return f"<TaskAssignment task={self.task_id} user={self.user_id}>"
