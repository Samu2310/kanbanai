from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, NotFoundException

# ─── Esquema OAuth2 ────────────────────────────────────────────────────────────
# tokenUrl indica a Swagger UI dónde está el endpoint de login.
# FastAPI lo usa para el botón "Authorize" en /docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependencia que extrae y valida el JWT del header Authorization.

    FastAPI llama a esto automáticamente cuando un endpoint lo declara:
        def mi_endpoint(payload: dict = Depends(get_current_user_payload)):
            user_id = payload["sub"]

    Retorna el payload decodificado si el token es válido.
    Lanza UnauthorizedException (401) si el token es inválido o expiró.

    NOTA: En Fase 3, se añadirá get_current_user() que usa este payload
    para buscar y retornar el objeto User completo desde la base de datos.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Token inválido o expirado.")
    return payload


def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que retorna el objeto User actual de la BD.
    """
    user_id_str = payload.get("sub")
    try:
        import uuid
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        from app.core.exceptions import UnauthorizedException
        raise UnauthorizedException("Token inválido (sub no es un UUID).")
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("Usuario no encontrado.")
    if not user.is_active:
        raise UnauthorizedException("El usuario está inactivo.")
    return user



def require_role(*allowed_roles: str):
    """
    Fábrica de dependencias para restringir endpoints por rol.

    Uso en un router:
        @router.get("/admin", dependencies=[Depends(require_role("professor"))])
        def endpoint_solo_profesores():
            ...

    Acepta múltiples roles:
        Depends(require_role("student", "professor"))

    NOTA: La implementación completa se finaliza en Fase 3 cuando
    get_current_user() esté disponible para leer el rol desde la BD.
    """
    def dependency(payload: dict = Depends(get_current_user_payload)):
        role = payload.get("role")
        if role not in allowed_roles:
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(
                f"Esta acción requiere uno de estos roles: {', '.join(allowed_roles)}"
            )
        return payload
    return dependency
