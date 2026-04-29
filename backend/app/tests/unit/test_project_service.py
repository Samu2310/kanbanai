import pytest
from app.schemas.project import ProjectCreate
# Mock del servicio y modelo para no usar base de datos en test unitario puro
# En FastAPI es común testear los endpoints con TestClient, 
# pero aquí verificamos lógica de negocio aislada.

def test_create_project_schema_validation():
    # Validar que Pydantic capture errores si faltan campos requeridos
    project_data = {
        "name": "Test Project",
        "description": "A great project"
    }
    project = ProjectCreate(**project_data)
    assert project.name == "Test Project"
    assert project.description == "A great project"

def test_create_project_schema_missing_name():
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        ProjectCreate(description="No name")
