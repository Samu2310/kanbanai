import pytest
from datetime import datetime, date, timedelta
from app.services.ai_service import analyze_kanban_board

class MockColumn:
    def __init__(self, id, name, wip_limit=None):
        self.id = id
        self.name = name
        self.wip_limit = wip_limit

class MockPriority:
    def __init__(self, value):
        self.value = value

class MockTask:
    def __init__(self, id, title, column_id, priority="medium", due_date=None, updated_at=None, assignments=None):
        self.id = id
        self.title = title
        self.column_id = column_id
        self.priority = MockPriority(priority)
        self.due_date = due_date
        self.updated_at = updated_at or datetime.utcnow()
        self.assignments = assignments or []
        self.owner_id = None

@pytest.fixture
def base_columns():
    return [
        MockColumn(id=1, name="To Do"),
        MockColumn(id=2, name="In Progress", wip_limit=3),
        MockColumn(id=3, name="Done")
    ]

def test_analyze_empty_board(base_columns):
    # Caso: Tablero sin tareas
    result = analyze_kanban_board([], base_columns)
    assert result["board_status"] == "ℹ️ El proyecto no tiene tareas todavía."
    assert len(result["alerts"]) == 1
    assert result["alerts"][0]["type"] == "info"

def test_analyze_wip_violation(base_columns):
    # Caso: Límite WIP superado en 'In Progress'
    tasks = [
        MockTask(id=1, title="T1", column_id=2),
        MockTask(id=2, title="T2", column_id=2),
        MockTask(id=3, title="T3", column_id=2),
        MockTask(id=4, title="T4", column_id=2), # Excede el WIP de 3
    ]
    result = analyze_kanban_board(tasks, base_columns)
    
    assert len(result["wip_violations"]) > 0
    assert any("supera su límite WIP" in v for v in result["wip_violations"])
    assert result["alerts"][0]["type"] == "danger"

def test_analyze_overdue_tasks(base_columns):
    # Caso: Tareas vencidas
    past_date = date.today() - timedelta(days=2)
    tasks = [
        MockTask(id=1, title="Tarea Vencida", column_id=2, due_date=past_date)
    ]
    result = analyze_kanban_board(tasks, base_columns)
    
    assert "overdue_tasks" in result or any("vencida" in act for act in result["priority_actions"])
    assert any("vencida" in a["message"] for a in result["alerts"])
    assert result["alerts"][0]["type"] == "danger"
    
def test_analyze_stagnant_tasks(base_columns):
    # Caso: Tareas estancadas por más de 5 días
    stagnant_date = datetime.utcnow() - timedelta(days=6)
    tasks = [
        MockTask(id=1, title="Tarea Estancada", column_id=2, updated_at=stagnant_date)
    ]
    result = analyze_kanban_board(tasks, base_columns)
    
    assert len(result["stagnant_tasks"]) == 1
    assert any("sin actividad" in a["message"] for a in result["alerts"])

def test_analyze_bottleneck(base_columns):
    # Caso: Cuello de botella absoluto (sin WIP)
    columns = [MockColumn(id=1, name="Backlog"), MockColumn(id=2, name="Testing")]
    tasks = [MockTask(id=i, title=f"T{i}", column_id=2) for i in range(11)] # 11 tareas en Testing
    
    result = analyze_kanban_board(tasks, columns)
    
    assert len(result["bottlenecks"]) > 0
    assert any("saturada" in b for b in result["bottlenecks"])

def test_analyze_json_structure(base_columns):
    # Caso: Estructura del JSON debe ser consistente
    result = analyze_kanban_board([], base_columns)
    
    expected_keys = ["board_status", "wip_violations", "bottlenecks", "stagnant_tasks", 
                     "flow_issues", "recommendations", "priority_actions", "alerts"]
    
    for key in expected_keys:
        assert key in result
