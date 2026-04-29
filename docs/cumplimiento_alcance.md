# Cumplimiento del Alcance del Proyecto

Este documento analiza de forma transparente el grado de cumplimiento de los objetivos definidos en el alcance del proyecto KanbanAI, enfocado en un entorno académico.

---

## ✅ 1. Gestión de estudiantes

**Contexto del Requisito:**
El sistema debe permitir gestionar a los estudiantes, asignar roles, involucrarlos en los proyectos y controlar qué tareas realizan dentro del tablero.

**Cómo lo cumple KanbanAI:**
* **Sistema de Roles y Autenticación:** El proyecto cuenta con un sistema robusto de inicio de sesión que clasifica a los usuarios en `student`, `professor`, `admin` y `guest`.
* **Asignación a Tareas:** Los usuarios pueden ser asignados como "responsables" de tareas individuales dentro del tablero Kanban.
* **Seguimiento (Historial):** Cualquier cambio de estado de una tarea (de Pendiente a Completada) genera un log en el historial asociando el cambio al usuario que lo realizó. Esto permite al profesor auditar quién movió qué tarea.
* **Evidencia:** Funcionalidad de login/registro (`auth.py`), asignación M:N de tareas (`models/task.py`) y registro de auditoría visual en el frontend.

**Limitaciones:**
Actualmente no existe un "panel de profesores" centralizado para ver el rendimiento cruzado de un estudiante en múltiples proyectos simultáneos; la gestión ocurre directamente observando los tableros y el historial de cambios de cada proyecto individual.

---

## ✅ 2. Evaluación

**Contexto del Requisito:**
El sistema debe proporcionar mecanismos para que los docentes o Scrum Masters puedan evaluar el progreso, la calidad o el estado del trabajo de los estudiantes.

**Cómo lo cumple KanbanAI:**
* **Feedback del Profesor:** El modelo de base de datos y la API incluyen el campo `teacher_feedback`, lo que permite dejar observaciones directas en las tareas y proyectos, facilitando una evaluación continua y no solo al final del semestre.
* **Scrum Master IA:** El motor heurístico evalúa de manera autónoma el desempeño del equipo, detectando tareas que llevan más de 5 días estancadas (Stagnant Tasks) y cuellos de botella. Esta evaluación automatizada ayuda a evidenciar problemas de flujo que el profesor puede observar sin auditar manualmente cada tarjeta.
* **Evidencia:** Endpoint `analyze_kanban_board` y el panel "Analizar Tablero" en la UI, más la columna `teacher_feedback` garantizada en la BD mediante Alembic.

**Limitaciones:**
La evaluación es cualitativa y enfocada en métricas ágiles. No emite un "grado numérico automático" ni se integra con un LMS (como Moodle).

---

## ✅ 3. Resultados

**Contexto del Requisito:**
El sistema debe reflejar entregables concretos, mostrar un avance claro del proyecto hacia un resultado final y proveer herramientas que asistan a lograr ese objetivo de forma eficiente.

**Cómo lo cumple KanbanAI:**
* **Flujo Kanban:** Toda la interfaz está diseñada para asegurar que el equipo mueva tareas desde *Pendiente* hacia *Done*. La interfaz gráfica ofrece resultados visuales inmediatos del estatus del proyecto.
* **Resultados Acelerados por IA:** Para vencer el bloqueo del escritor al iniciar un proyecto, la integración con *Google Gemini* genera los requisitos (tareas) a partir de descripciones naturales. Esto garantiza que los equipos comiencen a trabajar rápidamente con tareas bien dimensionadas y priorizadas.
* **Alertas de Resultado:** El Scrum Master inteligente reporta alertas como "El sprint está avanzado y la columna Done está vacía", garantizando el enfoque en resultados entregables.
* **Evidencia:** Pantalla de análisis de reportes, Generador de Tareas vía AI (`generate_tasks_from_text`), tablero general.

**Limitaciones:**
No genera gráficos de *Burn-down* o *Cumulative Flow Diagrams* nativos (usualmente presentes en herramientas empresariales complejas), reemplazando esta métrica por el diagnóstico textual inmediato del Scrum Master.

---

### Resumen
KanbanAI cumple íntegramente con el alcance propuesto. Logra equilibrar una herramienta de gestión tradicional con la asistencia de Inteligencia Artificial para ofrecer un software capaz de administrar estudiantes, facilitar su evaluación mediante métricas de flujo, y acelerar la obtención de resultados mediante asistencia algorítmica y generativa.
