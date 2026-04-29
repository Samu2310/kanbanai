import uuid
import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(str, enum.Enum):
    """Roles globales del sistema."""
    student = "student"
    professor = "professor"
    guest = "guest"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole"), nullable=False, default=UserRole.student
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relaciones ────────────────────────────────────────────────────────────
    owned_projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="owner", foreign_keys="Project.owner_id"
    )
    project_memberships: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="user", foreign_keys="ProjectMember.user_id"
    )
    created_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="creator", foreign_keys="Task.created_by"
    )
    task_assignments: Mapped[List["TaskAssignment"]] = relationship(
        "TaskAssignment", back_populates="user", foreign_keys="TaskAssignment.user_id"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", foreign_keys="Notification.user_id"
    )
    history_entries: Mapped[List["TaskHistory"]] = relationship(
        "TaskHistory", back_populates="changed_by_user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
