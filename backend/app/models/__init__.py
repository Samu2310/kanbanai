# ─── Importar todos los modelos en orden de dependencias ──────────────────────
# Este archivo es CRÍTICO para Alembic: al importar aquí, todos los modelos
# quedan registrados en Base.metadata y Alembic puede generar migraciones.
#
# ORDEN OBLIGATORIO (de menos a más dependiente):
#   1. User (sin dependencias de otros modelos)
#   2. Project, ProjectMember (depende de User)
#   3. BoardColumn (depende de Project)
#   4. Task, TaskAssignment (depende de Project, BoardColumn, User)
#   5. TaskHistory (depende de Task, User)
#   6. Notification (depende de User, Task)

from app.models.user import User, UserRole  # noqa: F401
from app.models.project import Project, ProjectMember, ProjectMemberRole  # noqa: F401
from app.models.column import BoardColumn, DEFAULT_COLUMNS  # noqa: F401
from app.models.task import Task, TaskAssignment, TaskPriority  # noqa: F401
from app.models.task_history import TaskHistory  # noqa: F401
from app.models.notification import Notification  # noqa: F401

