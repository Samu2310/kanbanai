import uuid
import enum
from datetime import datetime
from typing import Optional, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task
    from app.models.column import BoardColumn

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ProjectMemberRole(str, enum.Enum):
    """Rol de un usuario dentro de un proyecto específico."""
    owner = "owner"    # Creador del proyecto
    member = "member"  # Colaborador activo
    viewer = "viewer"  # Solo puede ver


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    teacher_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # updated_at se actualiza manualmente en el service layer
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relaciones ────────────────────────────────────────────────────────────
    owner: Mapped["User"] = relationship(
        "User", back_populates="owned_projects", foreign_keys=[owner_id]
    )
    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )
    columns: Mapped[List["BoardColumn"]] = relationship(
        "BoardColumn",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="BoardColumn.order",
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name}>"


class ProjectMember(Base):
    __tablename__ = "project_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role_in_project: Mapped[ProjectMemberRole] = mapped_column(
        SAEnum(ProjectMemberRole, name="projectmemberrole"),
        nullable=False,
        default=ProjectMemberRole.member,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relaciones ────────────────────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    user: Mapped["User"] = relationship(
        "User", back_populates="project_memberships", foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return (
            f"<ProjectMember project={self.project_id} "
            f"user={self.user_id} role={self.role_in_project}>"
        )
