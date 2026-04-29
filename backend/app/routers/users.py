from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene los datos del usuario actualmente autenticado.
    
    Este endpoint requiere enviar un token JWT válido en el header 
    Authorization (Bearer token).
    """
    return current_user
