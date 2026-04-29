from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.ai_service import analyze_tasks, summarize_project, generate_tasks_from_text, analyze_kanban_board, _analyze_tasks_fallback
from app.models.column import BoardColumn
from app.models.task import Task

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

class AnalyzeRequest(BaseModel):
    project_id: str

@router.post("/analyze", response_model=Dict[str, Any])
def analyze_board(request: AnalyzeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Analiza las tareas y devuelve recomendaciones."""
    import uuid as uuid_mod
    # ── Consulta a la BD ──────────────────────────────────────────────────────
    try:
        project_uuid = uuid_mod.UUID(str(request.project_id))
        columns = db.query(BoardColumn).filter(BoardColumn.project_id == project_uuid).all()
        tasks = db.query(Task).filter(Task.project_id == project_uuid).all()
    except Exception as e:
        return {
            "summary": "⚠️ No se pudo consultar el proyecto.",
            "risk_level": "low", "critical_tasks": [], "bottlenecks": [],
            "bottlenecks_count": 0,
            "recommendations": ["Verifica que el proyecto existe y tienes acceso."],
            "stagnant_tasks": [], "overdue_tasks": [],
            "alerts": [{"type": "warning", "message": f"Error en base de datos: {str(e)}"}]
        }

    # ── Análisis ──────────────────────────────────────────────────────────────
    try:
        board_analysis = analyze_kanban_board(tasks, columns)
        
        def _to_list(val):
            if isinstance(val, str): return [val]
            return val if isinstance(val, list) else []
        
        bottlenecks     = _to_list(board_analysis.get("bottlenecks", []))
        wip_violations  = _to_list(board_analysis.get("wip_violations", []))
        flow_issues     = _to_list(board_analysis.get("flow_issues", []))
        priority_actions = _to_list(board_analysis.get("priority_actions", []))
        recommendations = _to_list(board_analysis.get("recommendations", []))
        stagnant_tasks  = _to_list(board_analysis.get("stagnant_tasks", []))
        alerts = board_analysis.get("alerts", [])

        # Usar el risk_level calculado por el motor heurístico
        risk_level = board_analysis.get("_risk_level_computed", "low")
        
        critical_tasks_display = list(priority_actions)
        for b in bottlenecks:
            if b not in critical_tasks_display: critical_tasks_display.append(b)
        
        return {
            "summary": board_analysis.get("board_status", "Análisis completado."),
            "risk_level": risk_level,
            "critical_tasks": critical_tasks_display,
            "bottlenecks": bottlenecks,
            "bottlenecks_count": len(bottlenecks),
            "recommendations": recommendations,
            "stagnant_tasks": stagnant_tasks,
            "overdue_tasks": [],
            "alerts": alerts
        }
    except Exception as e:
        return {
            "summary": "⚠️ Error durante el análisis.",
            "risk_level": "low", "critical_tasks": [], "bottlenecks": [],
            "bottlenecks_count": 0,
            "recommendations": ["Revisa el tablero manualmente."],
            "stagnant_tasks": [], "overdue_tasks": [],
            "alerts": [{"type": "warning", "message": "No se pudo completar el análisis automático."}]
        }


class TextInput(BaseModel):
    text: str

@router.post("/generate-tasks", response_model=Dict[str, Any])
def generate_tasks_endpoint(input_data: TextInput, current_user: User = Depends(get_current_user)):
    """Genera tareas automáticamente a partir de texto libre."""
    if not input_data.text or not input_data.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")
    try:
        return generate_tasks_from_text(input_data.text.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al generar tareas.")
