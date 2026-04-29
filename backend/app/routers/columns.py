import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.column import ColumnRead
from app.models.column import BoardColumn
from app.services.project_service import get_project_by_id

router = APIRouter(prefix="/projects/{project_id}/columns", tags=["Columns"])

@router.get("", response_model=List[ColumnRead])
def get_columns(project_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtiene las columnas de un proyecto. 
    Verifica que el usuario sea miembro del proyecto.
    """
    # get_project_by_id valida la membresía del usuario o lanza 403 Forbidden
    get_project_by_id(db, project_id, current_user)
    
    columns = db.query(BoardColumn).filter(BoardColumn.project_id == project_id).order_by(BoardColumn.order).all()
    return columns
