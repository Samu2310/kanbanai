import json
import logging
import random
import time
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from app.schemas.task import TaskRead
from app.config import settings

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

if genai and settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _prio_val(task) -> str:
    prio = getattr(task, "priority", None)
    return getattr(prio, "value", str(prio)).lower() if prio else ""


def _days_since(dt_field, now_dt: datetime) -> Optional[int]:
    if dt_field is None:
        return None
    try:
        ts = dt_field.replace(tzinfo=None) if hasattr(dt_field, "replace") else dt_field
        return max(0, (now_dt - ts).days)
    except Exception:
        return None


def _pick(options: list) -> str:
    """Selecciona aleatoriamente entre variantes de texto para evitar repetición."""
    return random.choice(options)


# ---------------------------------------------------------------------------
# Función de compatibilidad legada
# ---------------------------------------------------------------------------
def _analyze_tasks_fallback(tasks: List[TaskRead], columns: List[Any] = None) -> Dict[str, Any]:
    if columns is None:
        columns = []

    now_date = date.today()
    now_dt = datetime.utcnow()

    critical_tasks, overdue_tasks, stagnant_tasks = [], [], []
    unassigned_count = 0
    high_priority_count = 0
    column_counts: Dict[str, int] = {}

    for task in tasks:
        cid = str(task.column_id)
        column_counts[cid] = column_counts.get(cid, 0) + 1

        if not task.assignments:
            unassigned_count += 1

        pv = _prio_val(task)
        if pv == "high":
            high_priority_count += 1

        if task.due_date and task.due_date < now_date:
            overdue_tasks.append(task)

        if task.updated_at:
            days = _days_since(task.updated_at, now_dt)
            if days is not None and days > 7:
                stagnant_tasks.append(task)

        if pv == "high" and task.due_date:
            days_to_due = (task.due_date - now_date).days

            if days_to_due < 0:
                overdue_tasks.append(task)  # ya vencida
            elif days_to_due <= 3:
                critical_tasks.append(task)

    column_limits = {str(c.id): getattr(c, "wip_limit", None) for c in columns}
    column_names  = {str(c.id): c.name for c in columns}

    bottlenecks, bottleneck_details = [], []
    for cid, count in column_counts.items():
        limit = column_limits.get(cid)
        name  = column_names.get(cid, "Desconocida")
        if limit is not None:
            if count >= limit:
                bottlenecks.append(cid)
                bottleneck_details.append(
                    f"La columna '{name}' tiene {count} tareas (límite WIP: {limit})."
                )
        elif count >= 5:
            bottlenecks.append(cid)
            bottleneck_details.append(f"La columna '{name}' acumula {count} tareas.")

    recommendations = []
    if overdue_tasks:
        recommendations.append(f"Hay {len(overdue_tasks)} tareas vencidas.")
    if stagnant_tasks:
        recommendations.append(
            f"Se detectaron {len(stagnant_tasks)} tareas estancadas sin actividad."
        )
    if bottleneck_details:
        recommendations.extend(bottleneck_details)
    if high_priority_count > len(tasks) * 0.5 and len(tasks) > 3:
        recommendations.append("Demasiadas tareas con 'Alta' prioridad. Revisar enfoque.")
    if unassigned_count > 0:
        recommendations.append(
            f"Existen {unassigned_count} tareas sin responsable asignado."
        )
    if not recommendations:
        recommendations.append(
            "¡Excelente! El proyecto fluye correctamente y sin riesgos detectados."
        )

    return {
        "critical_tasks": [t.title for t in critical_tasks],
        "overdue_tasks":  [t.title for t in overdue_tasks],
        "stagnant_tasks": [t.title for t in stagnant_tasks],
        "bottlenecks_count": len(bottlenecks),
        "recommendations": recommendations,
        "risk_level": (
            "High" if (critical_tasks or overdue_tasks or bottlenecks)
            else ("Medium" if (stagnant_tasks or unassigned_count > 0) else "Low")
        ),
    }


def analyze_tasks(tasks: List[TaskRead], columns: List[Any] = None) -> Dict[str, Any]:
    return _analyze_tasks_fallback(tasks, columns)


def summarize_project(tasks: List[TaskRead]) -> Dict[str, Any]:
    total_tasks = len(tasks)
    if total_tasks == 0:
        return {"summary": "El proyecto no tiene tareas actualmente."}

    high_priority = sum(1 for t in tasks if _prio_val(t) == "high")
    column_counts: Dict[str, int] = {}
    for task in tasks:
        cid = str(task.column_id)
        column_counts[cid] = column_counts.get(cid, 0) + 1

    overdue = sum(1 for t in tasks if t.due_date and t.due_date < date.today())
    summary_text = (
        f"El proyecto cuenta con {total_tasks} tareas. "
        f"{high_priority} de alta prioridad y {overdue} atrasadas. "
        f"Distribuidas en {len(column_counts)} columnas."
    )
    return {
        "total_tasks": total_tasks,
        "high_priority_count": high_priority,
        "overdue_count": overdue,
        "summary": summary_text,
    }


def generate_tasks_from_text(text: str) -> dict:
    """
    Genera entre 4 y 7 tareas Kanban a partir de texto libre usando Gemini.

    - Usa un prompt detallado en español orientado a gestión de proyectos.
    - Valida cada tarea generada (título, descripción, prioridad válida).
    - Si la API falla o no está configurada, devuelve un fallback de 5 tareas
      genéricas pero coherentes con las fases típicas de un proyecto.
    """
    VALID_PRIORITIES = {"high", "medium", "low"}

    # ── Fallback enriquecido con fases reales de proyecto ─────────────────────
    short_text = text[:80].strip()
    fallback_response = {
        "tasks": [
            {
                "title": "Planificación y alcance",
                "description": (
                    f"Definir el alcance, objetivos y criterios de éxito para: {short_text}."
                ),
                "priority": "high",
            },
            {
                "title": "Relevamiento de requerimientos",
                "description": (
                    "Identificar y documentar todos los requerimientos funcionales "
                    "y no funcionales del proyecto."
                ),
                "priority": "high",
            },
            {
                "title": "Diseño de solución",
                "description": (
                    "Crear el diseño técnico y de experiencia de usuario "
                    "que guíe la implementación."
                ),
                "priority": "medium",
            },
            {
                "title": "Implementación",
                "description": (
                    "Desarrollar las funcionalidades definidas siguiendo "
                    "las especificaciones acordadas."
                ),
                "priority": "medium",
            },
            {
                "title": "Pruebas y validación",
                "description": (
                    "Ejecutar pruebas funcionales, de integración y de aceptación "
                    "para garantizar la calidad."
                ),
                "priority": "low",
            },
        ]
    }

    # ── Sin API KEY o sin librería → fallback inmediato ────────────────────────
    if not settings.GEMINI_API_KEY or not genai:
        logger.warning("Gemini no configurado. Usando fallback de generate_tasks_from_text.")
        return fallback_response

    # ── Prompt mejorado: Scrum Master + Kanban expert ─────────────────────────
    prompt = f"""Eres un experto en gestión de proyectos ágiles (Scrum + Kanban).

Analiza el siguiente requerimiento:

\"{text}\"

Genera tareas base realistas para iniciar el proyecto.

Reglas:
- Entre 4 y 7 tareas
- Orden lógico: análisis → diseño → implementación → pruebas → despliegue
- Adaptadas al tipo de proyecto (no genéricas ni repetitivas)
- Títulos concretos y accionables (máximo 8 palabras)
- Descripciones breves pero útiles (1-2 oraciones)
- Prioridad correcta: "high", "medium" o "low"

Formato obligatorio (SOLO el JSON, sin texto adicional):
{{
  "tasks": [
    {{
      "title": "string",
      "description": "string",
      "priority": "low | medium | high"
    }}
  ]
}}

NO agregues texto fuera del JSON."""

    # ── Modelos a intentar en orden de preferencia (serie 3.1 / 2.5) ───────────
    MODEL_CANDIDATES = [
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
    ]

    gen_config = genai.types.GenerationConfig(
        temperature=0.6,
        max_output_tokens=1024,
    )

    raw = ""  # para capturar en JSONDecodeError aunque falle antes

    for model_name in MODEL_CANDIDATES:
        for attempt in range(2):
            try:
                if attempt == 0:
                    print(f"Intentando modelo: {model_name}")
                    logger.info(f"Intentando modelo Gemini: {model_name}")
                
                model = genai.GenerativeModel(model_name, generation_config=gen_config)
                api_response = model.generate_content(prompt)
                raw = api_response.text.strip()

                # ── Limpiar bloques markdown ───────────────────────────────────────
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0].strip()
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0].strip()

                parsed = json.loads(raw)

                # ── Validar estructura ─────────────────────────────────────────────
                if not isinstance(parsed, dict) or "tasks" not in parsed:
                    raise ValueError("Respuesta sin clave 'tasks'.")

                validated_tasks = []
                for task in parsed["tasks"]:
                    title       = str(task.get("title", "")).strip()
                    description = str(task.get("description", "")).strip()
                    priority    = str(task.get("priority", "medium")).strip().lower()

                    if not title:
                        continue
                    if priority not in VALID_PRIORITIES:
                        priority = "medium"

                    validated_tasks.append({
                        "title":       title,
                        "description": description or "Sin descripción.",
                        "priority":    priority,
                    })

                if not validated_tasks:
                    raise ValueError("Lista de tareas vacía tras validación.")

                logger.info(f"Tareas generadas con {model_name}: {len(validated_tasks)}")
                print(f"Modelo exitoso: {model_name} ({len(validated_tasks)} tareas)")
                return {"tasks": validated_tasks[:7]}

            except json.JSONDecodeError as e:
                print(f"Fallo modelo: {model_name} (JSON inválido)")
                logger.error(f"[{model_name}] JSON inválido: {e} | Raw: {raw[:200]}")
                break  # Error no recuperable, pasa al siguiente modelo
            except Exception as e:
                err_msg = str(e).lower()
                
                # Manejo de rate limit
                if any(k in err_msg for k in ["quota", "rate limit", "429", "retry_delay"]):
                    if attempt == 0:
                        print("Rate limit detectado, esperando 15s...")
                        time.sleep(15)
                        print(f"Reintentando modelo: {model_name}")
                        continue
                    else:
                        print(f"Fallo modelo tras reintento: {model_name} (Rate Limit)")
                        logger.error(f"[{model_name}] Rate limit persistente.")
                        break

                if "404" in err_msg or "not found" in err_msg:
                    print(f"Fallo modelo: {model_name} (404 - no disponible)")
                    logger.warning(f"[{model_name}] Modelo no disponible, probando siguiente...")
                    break
                    
                print(f"Fallo modelo: {model_name} ({err_msg[:80]})")
                logger.error(f"[{model_name}] Error: {err_msg}")
                break

    # Si ningún modelo funcionó → fallback
    print("Todos los modelos Gemini fallaron. Usando fallback interno.")
    logger.error("Todos los modelos Gemini fallaron. Usando fallback interno.")
    return fallback_response


# ===========================================================================
#  MOTOR HEURÍSTICO SCRUM MASTER  ·  analyze_kanban_board
# ===========================================================================

def analyze_kanban_board(tasks: list, columns: list) -> dict:
    """
    Motor heurístico avanzado estilo Scrum Master real.

    Detecta:
    - Violaciones WIP (con y sin límite explícito)
    - Cuellos de botella relativos entre columnas
    - Flujo bloqueado (push sin pull, backlog inflado)
    - Tareas estancadas (5+ días sin cambio, calibrado para evitar falsos positivos)
    - Tareas vencidas / próximas a vencer
    - Sobrecarga individual por persona
    - Inflación de prioridad alta
    - Tareas activas sin responsable
    - Columna Done vacía con sprint avanzado
    - Tareas de alta prioridad atascadas en backlog

    Umbrales calibrados para evitar falsos positivos en tableros pequeños.
    Compatible con objetos ORM de SQLAlchemy.
    Devuelve el esquema estándar sin romper el router ni el frontend.
    """
    if not columns:
        columns = []

    now_dt   = datetime.utcnow()
    now_date = date.today()

    # ── Umbrales calibrados — ajusta aquí si necesitas más/menos sensibilidad ──
    STAGNANT_DAYS          = 5    # días sin actividad para considerar estancada
    OVERLOAD_THRESHOLD     = 5    # tareas activas por persona para alertar sobrecarga
    BOTTLENECK_WARN_ABS    = 3    # tareas en columna sin WIP limit para warning
    BOTTLENECK_DANGER_ABS  = 6    # tareas en columna sin WIP limit para danger
    HIGH_PRIO_RATIO        = 0.6  # porcentaje de alta prioridad para alertar inflación
    HIGH_PRIO_MIN_TASKS    = 4    # mínimo de tareas totales para evaluar inflación
    BACKLOG_HIGH_PRIO_MIN  = 2    # alta prioridad en backlog para alertar
    BACKLOG_INFLATED_MIN   = 4    # tareas en backlog para considerar inflado
    DONE_EMPTY_SPRINT_MIN  = 6    # tareas totales para alertar Done vacío
    BOTTLENECK_REL_RATIO   = 2    # columna X veces más grande que la siguiente
    BOTTLENECK_REL_MIN     = 3    # mínimo en columna actual para alerta relativa

    response: dict = {
        "board_status":    "El tablero fluye adecuadamente.",
        "wip_violations":  [],
        "bottlenecks":     [],
        "stagnant_tasks":  [],
        "flow_issues":     [],
        "recommendations": [],
        "priority_actions":[],
        "alerts":          [],
    }

    try:
        total_tasks = len(tasks)

        # ── 0. Tablero vacío ───────────────────────────────────────────────────
        if total_tasks == 0:
            response["board_status"] = "ℹ️ El proyecto no tiene tareas todavía."
            response["alerts"].append({
                "type": "info",
                "message": "No hay tareas. Crea al menos una para comenzar el sprint.",
            })
            return response

        # ── 1. Mapas base ──────────────────────────────────────────────────────
        col_order = {str(c.id): i for i, c in enumerate(columns)}
        col_name  = {str(c.id): c.name for c in columns}
        col_wip   = {str(c.id): getattr(c, "wip_limit", None) for c in columns}
        col_count: Dict[str, int] = {str(c.id): 0 for c in columns}

        for t in tasks:
            cid = str(t.column_id)
            if cid in col_count:
                col_count[cid] += 1

        n_cols      = len(columns)
        cols_sorted = sorted(columns, key=lambda c: col_order.get(str(c.id), 99))
        first_cid   = str(cols_sorted[0].id)  if cols_sorted else None
        last_cid    = str(cols_sorted[-1].id) if cols_sorted else None

        # Columnas activas (excluye primera y última para algunos cálculos)
        active_col_ids = {
            str(c.id) for i, c in enumerate(cols_sorted)
            if i > 0 and i < n_cols - 1
        }

        # ── 2. Contadores generales y listas detalladas ────────────────────────
        overdue_list:   List[str] = []
        critical_list:  List[str] = []   # alta prioridad + vence en ≤3 días
        stagnant_list:  List[str] = []
        high_prio_count   = 0
        high_prio_backlog = 0            # alta prioridad atascada en columna inicial
        person_load: Dict[str, int] = {} # responsable → nº tareas activas
        unassigned_active = 0

        for t in tasks:
            cid   = str(t.column_id)
            pv    = _prio_val(t)
            order = col_order.get(cid, -1)
            is_done   = (cid == last_cid)
            is_active = not is_done
            # Columnas intermedias (ni backlog ni done)
            is_middle = cid in active_col_ids

            # Prioridad alta
            if pv == "high":
                high_prio_count += 1
                # Solo cuenta como "atascada en backlog" si lleva más de 2 días
                # sin moverse (evita falso positivo en tareas recién creadas)
                if cid == first_cid:
                    days_in_backlog = _days_since(getattr(t, "updated_at", None), now_dt)
                    if days_in_backlog is None or days_in_backlog >= 2:
                        high_prio_backlog += 1

            # Tareas vencidas (solo activas)
            due = getattr(t, "due_date", None)
            if due and due < now_date and is_active:
                overdue_list.append(
                    f"'{t.title}' (vencida el {due.strftime('%d/%m/%Y')})"
                )

            # Tareas críticas: alta prioridad + vence en ≤3 días (activas)
            # IMPORTANTE: excluir tareas ya vencidas (days_left < 0) para evitar
            # duplicación de señales — las vencidas ya están en overdue_list
            # y tendrán mayor prioridad en priority_actions.
            if pv == "high" and due and is_active:
                days_left = (due - now_date).days
                if 0 <= days_left <= 3:   # solo futuro inmediato, nunca pasado
                    critical_list.append(
                        f"'{t.title}' vence en {days_left}d — acción urgente"
                    )

            # Tareas estancadas — umbral aumentado a STAGNANT_DAYS para reducir ruido
            upd_days = _days_since(getattr(t, "updated_at", None), now_dt)
            if upd_days is not None and upd_days >= STAGNANT_DAYS and is_active:
                c_name = col_name.get(cid, "Desconocida")
                stagnant_list.append(
                    f"'{t.title}' — {upd_days}d sin cambios en '{c_name}'"
                )

            # Carga por persona (solo columnas activas, excluye Done)
            assignments = getattr(t, "assignments", None) or []
            # Detectar responsable real (no solo assignments)
            has_owner = False
            # Caso 1: assignments (relación many-to-many)
            if assignments:
                has_owner = True
            # Caso 2: campo directo tipo owner / user_id
            elif getattr(t, "owner_id", None) or getattr(t, "user_id", None):
                has_owner = True
            # Caso 3 (opcional): objeto user directo
            elif getattr(t, "user", None):
                has_owner = True
            if is_active:
                # Solo contar como sin responsable si realmente NO hay dueño
                if not has_owner and is_middle:
                    unassigned_active += 1            
            for asgn in assignments:
                    user = getattr(asgn, "user", None)
                    name = (
                        getattr(user, "full_name", None)
                        or getattr(user, "username", None)
                        or getattr(user, "email", None)
                        or str(getattr(asgn, "user_id", "?"))
                    )
                    person_load[name] = person_load.get(name, 0) + 1

        overdue_count  = len(overdue_list)
        stagnant_count = len(stagnant_list)
        response["stagnant_tasks"] = stagnant_list

        # ── 3. WIP violations y cuellos de botella ─────────────────────────────
        for c in columns:
            cid   = str(c.id)
            count = col_count.get(cid, 0)
            name  = col_name.get(cid, "Desconocida")
            limit = col_wip.get(cid)
            is_done_col = (cid == last_cid)

            if count == 0:
                continue

            # No analizar cuello de botella en columna Done (acumulación es normal)
            if is_done_col:
                continue

            if limit is not None and count > limit:
                # Violación WIP explícita — siempre es un problema real
                excess = count - limit
                msg = (
                    f"⛔ '{name}' supera su límite WIP: {count}/{limit} tareas "
                    f"({excess} en exceso). El flujo está bloqueado."
                )
                response["wip_violations"].append(msg)
                response["alerts"].append({"type": "danger", "message": msg})
                response["priority_actions"].append(
                    f"Completar o mover {excess} tarea(s) de '{name}' antes de agregar trabajo nuevo."
                )

            elif limit is None:
                # Sin WIP limit: usar umbrales absolutos calibrados
                if count >= BOTTLENECK_DANGER_ABS:
                    msg = (
                        f"🔴 '{name}' está saturada: {count} tareas acumuladas. "
                        f"El equipo no puede absorber más trabajo aquí."
                    )
                    response["bottlenecks"].append(msg)
                    response["alerts"].append({"type": "danger", "message": msg})
                    response["priority_actions"].append(
                        f"URGENTE: terminar tareas en '{name}' antes de iniciar nuevas."
                    )
                elif count >= BOTTLENECK_WARN_ABS:
                    msg = (
                        f"🟡 '{name}' acumula {count} tareas. "
                        f"Riesgo latente de cuello de botella."
                    )
                    response["bottlenecks"].append(msg)
                    response["alerts"].append({"type": "warning", "message": msg})
                    response["recommendations"].append(
                        f"Revisar '{name}': verifica si hay bloqueos o dependencias sin resolver."
                    )

        # ── 4. Cuello de botella relativo (columna >> siguiente) ───────────────
        # Solo entre columnas NO-Done. Ratio calibrado para evitar falsos positivos
        # en tableros pequeños.
        for i in range(len(cols_sorted) - 2):  # excluye la última (Done)
            curr   = cols_sorted[i]
            nxt    = cols_sorted[i + 1]
            curr_c = col_count.get(str(curr.id), 0)
            nxt_c  = col_count.get(str(nxt.id), 0)

            # Solo alertar si la columna actual supera el mínimo absoluto
            # Y es BOTTLENECK_REL_RATIO veces mayor que la siguiente
            # (antes era 2x+1, lo que disparaba con 3 vs 1)
            if curr_c >= BOTTLENECK_REL_MIN and curr_c >= nxt_c * BOTTLENECK_REL_RATIO:
                msg = (
                    f"🔀 Trabajo estancado: '{curr.name}' tiene {curr_c} tareas "
                    f"mientras '{nxt.name}' sólo tiene {nxt_c}. "
                    f"El flujo no avanza."
                )
                if msg not in response["flow_issues"]:
                    response["flow_issues"].append(msg)
                    response["alerts"].append({"type": "warning", "message": msg})
                    response["recommendations"].append(
                        _pick([
                            f"Aplicar sistema Pull en '{curr.name}': "
                            f"terminar antes de iniciar.",
                            f"Limitar la entrada a '{curr.name}' hasta que "
                            f"'{nxt.name}' libere capacidad.",
                            f"Hacer una sesión de debloqueo en '{curr.name}' "
                            f"para identificar impedimentos.",
                        ])
                    )

        # ── 5. Backlog inflado ─────────────────────────────────────────────────
        # Solo alerta si el backlog es grande EN TÉRMINOS ABSOLUTOS, no relativo
        # a Done (que puede estar vacío en inicio de sprint sin ser un problema).
        if first_cid and n_cols >= 3:
            first_count = col_count.get(first_cid, 0)
            done_count  = col_count.get(last_cid, 0) if last_cid else 0
            # Alerta solo si backlog supera el umbral absoluto Y hay tareas en curso
            # (suma de columnas intermedias > 0, para no alertar en tablero nuevo)
            in_progress = sum(
                col_count.get(str(c.id), 0)
                for c in cols_sorted[1:-1]
            )
            if first_count >= BACKLOG_INFLATED_MIN and in_progress > 0:
                msg = (
                    f"📥 Backlog inflado: {first_count} tareas pendientes. "
                    f"El equipo puede estar acumulando trabajo sin terminar."
                )
                response["flow_issues"].append(msg)
                response["alerts"].append({"type": "warning", "message": msg})
                response["recommendations"].append(
                    "Priorizar terminar tareas en curso antes de agregar nuevas al tablero."
                )

        # ── 6. Alta prioridad atascada en backlog ──────────────────────────────
        # Umbral aumentado a BACKLOG_HIGH_PRIO_MIN para reducir ruido
        if high_prio_backlog >= BACKLOG_HIGH_PRIO_MIN:
            msg = (
                f"🚨 {high_prio_backlog} tarea(s) de ALTA prioridad llevan "
                f"tiempo en el backlog sin ser iniciadas."
            )
            response["flow_issues"].append(msg)
            response["alerts"].append({"type": "danger", "message": msg})
            response["priority_actions"].insert(
                0,
                f"Iniciar inmediatamente las {high_prio_backlog} tareas urgentes "
                f"que están bloqueadas en el backlog.",
            )

        # ── 7. Tareas vencidas ─────────────────────────────────────────────────
        # Siempre 'danger' (1 tarea vencida ya es una promesa rota).
        # Siempre en posición [0] de priority_actions para garantizar máxima visibilidad.
        if overdue_count > 0:
            sample    = overdue_list[:2]
            names_str = ", ".join(sample) + (" y más..." if overdue_count > 2 else "")
            msg = f"📅 {overdue_count} tarea(s) con fecha límite vencida: {names_str}."
            response["alerts"].insert(0, {"type": "danger", "message": msg})
            response["priority_actions"].insert(
                0,
                f"🔴 URGENTE: {overdue_count} tarea(s) vencida(s) — "
                f"atender hoy o renegociar fecha con el cliente.",
            )

        # ── 8. Tareas críticas (alta prio + vence pronto) ─────────────────────
        if critical_list:
            names_str = "; ".join(critical_list[:3])
            msg = f"⚡ Tareas críticas próximas a vencer: {names_str}."
            response["alerts"].append({"type": "danger", "message": msg})
            response["priority_actions"].append(
                "Enfoca al equipo en las tareas críticas antes de cualquier otra cosa."
            )

        # ── 9. Tareas estancadas ───────────────────────────────────────────────
        if stagnant_count > 0:
            msg = (
                f"💤 {stagnant_count} tarea(s) sin actividad en {STAGNANT_DAYS}+ días. "
                f"¿Hay bloqueos ocultos o falta de claridad?"
            )
            response["alerts"].append({"type": "warning", "message": msg})
            response["recommendations"].append(
                _pick([
                    f"Revisar en la próxima Daily las {stagnant_count} tareas "
                    f"estancadas e identificar impedimentos.",
                    f"Las {stagnant_count} tareas sin movimiento necesitan "
                    f"un responsable o una decisión de cierre.",
                    f"Escalar las {stagnant_count} tareas paralizadas: "
                    f"¿hay dependencias externas bloqueando el avance?",
                ])
            )

        # ── 10. Tareas activas sin responsable ─────────────────────────────────
        # Solo cuenta las de columnas intermedias (en progreso real).
        # Señal secundaria: solo se muestra si hay 3 o más, como 'info' (no 'warning')
        # para que NO eleve el risk_level ni tape problemas más importantes.
        if unassigned_active >= 3:
            # Solo agregar recomendación opcional si no hay muchas ya
            if len(response["recommendations"]) < 3:
                response["recommendations"].append(
                    f"Opcional: asignar responsable a {unassigned_active} tarea(s) activas."
                )

        # ── 11. Sobrecarga individual ──────────────────────────────────────────
        # Umbral aumentado a OVERLOAD_THRESHOLD para evitar alertas en equipos pequeños
        overloaded = {p: n for p, n in person_load.items() if n >= OVERLOAD_THRESHOLD}
        if overloaded:
            for person, n in overloaded.items():
                msg = (
                    f"🧑‍💻 '{person}' tiene {n} tareas activas asignadas. "
                    f"Riesgo real de burnout y bloqueo."
                )
                response["flow_issues"].append(msg)
                response["alerts"].append({"type": "warning", "message": msg})
                response["recommendations"].append(
                    f"Redistribuir al menos {n - (OVERLOAD_THRESHOLD - 1)} tarea(s) de '{person}' "
                    f"a otros miembros del equipo."
                )

        # ── 12. Inflación de prioridad alta ────────────────────────────────────
        # Umbrales ajustados: requiere más tareas totales y un ratio más alto
        # para evitar que proyectos pequeños disparen esta alerta innecesariamente
        if total_tasks >= HIGH_PRIO_MIN_TASKS and high_prio_count > total_tasks * HIGH_PRIO_RATIO:
            pct = int(high_prio_count / total_tasks * 100)
            msg = (
                f"⚠️ {high_prio_count}/{total_tasks} tareas ({pct}%) marcadas como "
                f"'Alta' prioridad. Cuando todo es urgente, nada lo es."
            )
            response["flow_issues"].append(msg)
            response["alerts"].append({"type": "warning", "message": msg})
            response["recommendations"].append(
                "Hacer una sesión de repriorización: reserva 'Alta' solo para "
                "lo que realmente impacta al cliente o al sprint."
            )

        # ── 13. Done vacío con sprint avanzado ─────────────────────────────────
        # Solo alerta si hay suficientes tareas Y hay trabajo en columnas intermedias
        # (evita falso positivo al inicio del sprint cuando todo está en backlog)
        if last_cid and col_count.get(last_cid, 0) == 0 and total_tasks >= DONE_EMPTY_SPRINT_MIN:
            in_progress = sum(
                col_count.get(str(c.id), 0)
                for c in cols_sorted[1:-1]
            )
            # Solo alertar si hay trabajo activo en columnas intermedias
            # (indica que el sprint avanzó pero nada llegó a Done)
            if in_progress >= 3:
                msg = (
                    "🏁 Ninguna tarea ha llegado a 'Done' aún. "
                    "El equipo trabaja mucho pero sin cerrar entregables."
                )
                response["flow_issues"].append(msg)
                response["alerts"].append({"type": "warning", "message": msg})
                response["recommendations"].append(
                    "Foco en terminar: elige 1-2 tareas más cercanas a Done "
                    "y llévalas hasta el final antes de iniciar nuevas."
                )

        # ── 14. Calcular nivel de riesgo global ────────────────────────────────
        danger_alerts  = [a for a in response["alerts"] if a["type"] == "danger"]
        warning_alerts = [a for a in response["alerts"] if a["type"] == "warning"]

        if danger_alerts or overdue_count >= 2 or critical_list:
            risk_level = "high"
        elif warning_alerts or overdue_count >= 1 or stagnant_count >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        # ── 15. Board status descriptivo y contextual ──────────────────────────
        n_danger  = len(danger_alerts)
        n_warning = len(warning_alerts)

        if risk_level == "high":
            worst_problems = (
                response["wip_violations"]
                or response["priority_actions"]
                or response["bottlenecks"]
            )
            context = worst_problems[0].split(".")[0] if worst_problems else (
                f"{overdue_count} tarea(s) vencida(s)" if overdue_count else "múltiples bloqueos"
            )
            response["board_status"] = _pick([
                f"🔴 Tablero en estado crítico: {n_danger} problema(s) grave(s) detectado(s). "
                f"{context}. Se requiere intervención inmediata del equipo.",
                f"🔴 Intervención urgente: hay {n_danger} alerta(s) crítica(s) activas. "
                f"El sprint está en riesgo de fracasar si no se actúa hoy.",
                f"🔴 Situación de riesgo alto: {context}. "
                f"El equipo debe parar, revisar el tablero y resolver los bloqueos.",
            ])

        elif risk_level == "medium":
            context_src = (
                response["flow_issues"]
                or response["bottlenecks"]
                or response["stagnant_tasks"]
            )
            context = context_src[0].split(".")[0] if context_src else "varias señales de alerta"
            response["board_status"] = _pick([
                f"🟡 El tablero necesita atención: {n_warning} señal(es) de alerta. "
                f"{context}. Revisa las recomendaciones.",
                f"🟡 Flujo en riesgo: se detectaron {n_warning} punto(s) débiles. "
                f"Actúa antes de que se conviertan en bloqueos críticos.",
                f"🟡 Situación bajo control, pero con tensión: {context}. "
                f"Gestiona las alertas en el próximo Daily.",
            ])

        else:
            response["board_status"] = _pick([
                "✅ Tablero en buen estado. El equipo mantiene un flujo saludable. ¡Sigan así!",
                "✅ Excelente ritmo de trabajo. Sin bloqueos detectados. "
                "Continúen respetando el sistema Pull.",
                "✅ El sprint avanza correctamente. "
                "Ningún indicador crítico activo. Mantén el enfoque.",
            ])
            response["alerts"].append({
                "type": "info",
                "message": "Buen ritmo de trabajo. Continúa respetando el flujo Kanban.",
            })

        # ── 16. Recomendación positiva si no hay nada negativo ─────────────────
        if not response["recommendations"]:
            response["recommendations"].append(
                _pick([
                    "Mantén el ritmo actual. Aplica el sistema Pull: termina antes de iniciar.",
                    "El equipo está en zona de alto rendimiento. Protege el foco y evita interrupciones.",
                    "Sin puntos de mejora urgentes. Considera reducir el WIP limit para acelerar aún más.",
                ])
            )

        # ── 17. Limitar listas para no saturar el frontend ─────────────────────
        response["stagnant_tasks"]   = response["stagnant_tasks"][:8]
        response["recommendations"]  = response["recommendations"][:6]
        response["priority_actions"] = response["priority_actions"][:5]
        response["flow_issues"]      = response["flow_issues"][:5]
        response["bottlenecks"]      = response["bottlenecks"][:5]
        response["wip_violations"]   = response["wip_violations"][:5]

        # Metadato interno para el router
        response["_risk_level_computed"] = risk_level

    except Exception as e:
        logger.error(f"Error crítico en analyze_kanban_board: {e}", exc_info=True)
        response["board_status"] = "⚠️ Error interno en el análisis. Revisión manual requerida."
        response["alerts"] = [{"type": "warning", "message": f"Error de análisis: {str(e)}"}]

    return response

