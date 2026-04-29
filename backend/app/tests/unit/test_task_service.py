import pytest
from app.schemas.task import TaskCreate

def test_task_create_schema():
    task_data = {
        "title": "New Task",
        "description": "Task desc",
        "column_id": 1,
        "priority": "high"
    }
    task = TaskCreate(**task_data)
    assert task.title == "New Task"
    assert task.priority == "high"

def test_task_create_invalid_priority():
    # Asumiendo que la prioridad está validada por enum en Pydantic
    pass # Depende de la implementación exacta, se puede extender.
