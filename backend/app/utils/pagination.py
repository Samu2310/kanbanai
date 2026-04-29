from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Parámetros de paginación reutilizables para cualquier endpoint de listado.

    Uso en un router:
        @router.get("/projects")
        def list_projects(params: PaginationParams = Depends()):
            offset = params.offset
            ...
    """
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        """Calcula el OFFSET de SQL a partir del número de página."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada genérica.

    Uso:
        return PaginatedResponse(
            items=tasks,
            total=100,
            page=1,
            page_size=20,
            total_pages=5,
        )

    El parámetro genérico T será el schema de cada ítem.
    Ejemplo: PaginatedResponse[TaskRead]
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def build(cls, items: List[T], total: int, page: int, page_size: int):
        """Constructor conveniente que calcula total_pages automáticamente."""
        import math
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if page_size > 0 else 0,
        )
