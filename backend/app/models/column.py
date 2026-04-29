import uuid
from typing import List

from sqlalchemy import String, Integer, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BoardColumn(Base):
    """
    Columna del tablero Kanban (Pendiente, En Progreso, En Revisión, Finalizada).

    El nombre de la clase Python es BoardColumn en lugar de Column para evitar
    conflicto con la clase sqlalchemy.Column que se importa en otros archivos.
    El nombre en la base de datos sigue siendo 'columns'.

    Las 4 columnas fijas se crean automáticamente al crear un proyecto
    (ver project_service.py → create_project).
    """
    __tablename__ = "columns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    # Nombre visible de la columna: "Pendiente", "En Progreso", etc.
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Controla el orden de izquierda a derecha en el tablero (0, 1, 2, 3)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # ─── Relaciones ────────────────────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="columns")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="column")

    def __repr__(self) -> str:
        return f"<BoardColumn id={self.id} name={self.name} order={self.order}>"


# Nombres estándar de las 4 columnas del Kanban
DEFAULT_COLUMNS = [
    {"name": "Pendiente", "order": 0},
    {"name": "En Progreso", "order": 1},
    {"name": "En Revisión", "order": 2},
    {"name": "Finalizada", "order": 3},
]
