from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Error 404 — El recurso solicitado no existe en la base de datos.
    Uso: raise NotFoundException("Tarea no encontrada")
    """
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(HTTPException):
    """
    Error 401 — El usuario no está autenticado o el token es inválido.
    Incluye el header WWW-Authenticate requerido por el estándar OAuth2.
    """
    def __init__(self, detail: str = "No autenticado. Proporciona un token válido."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    """
    Error 403 — El usuario está autenticado pero no tiene permiso para esta acción.
    Diferencia clave con 401: aquí el usuario SÍ está identificado, pero su rol
    no le permite la operación.
    """
    def __init__(self, detail: str = "No tienes permiso para realizar esta acción."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(HTTPException):
    """
    Error 409 — El recurso ya existe o hay un conflicto de estado.
    Ejemplo: intentar registrar un email que ya está en uso.
    """
    def __init__(self, detail: str = "Conflicto con el estado actual del recurso."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class BadRequestException(HTTPException):
    """
    Error 400 — La solicitud tiene datos inválidos o mal formados.
    Ejemplo: mover una tarea a una columna que no pertenece al mismo proyecto.
    """
    def __init__(self, detail: str = "Solicitud inválida."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
