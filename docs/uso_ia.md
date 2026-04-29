# Uso de Inteligencia Artificial en KanbanAI

El proyecto KanbanAI implementa una filosofía híbrida de "Inteligencia". Combina la potencia del procesamiento de lenguaje natural externo con un motor experto (heurístico) interno y ultrarrápido.

Esta arquitectura separa el sistema en **dos módulos distintos**:

---

## 1. El Scrum Master Virtual (Motor Heurístico Local)

El análisis del tablero y detección de riesgos del proyecto **NO** utiliza APIs externas ni IA Generativa. Está construido internamente utilizando programación heurística pura.

### ¿Por qué heurístico y no LLM (Gemini)?
* **Cero Latencia:** Evalúa tableros con miles de tareas en milisegundos.
* **Cero Costo:** No consume tokens de API.
* **Determinismo:** Los consejos de agilidad no "alucinan"; están codificados basados en mejores prácticas reales de la industria (Scrum/Kanban).
* **Privacidad:** La información de progreso y rendimiento de los usuarios nunca abandona el servidor.

### ¿Qué detecta el Motor Heurístico?
El motor (`backend/app/services/ai_service.py`) escanea los objetos en memoria y dispara alertas basadas en umbrales precisos:
1. **Cuellos de Botella Absolutos:** Si una columna supera las 6 tareas (para un equipo pequeño), lanza una alerta roja.
2. **Cuellos de Botella Relativos:** Detecta "trabajo estancado" si una columna tiene el doble de tareas que la siguiente.
3. **Violaciones WIP:** Avisa si se rompen los límites de Trabajo en Progreso (Work In Progress) configurados por el usuario.
4. **Sobrecarga Individual:** Detecta si un usuario tiene más de 5 tareas asignadas de forma simultánea.
5. **Backlog Inflado y Tareas Estancadas:** Encuentra tareas que no se han movido en 5+ días.
6. **Prioridades Críticas:** Levanta tareas de alta prioridad que están próximas a vencer.

---

## 2. Generación de Tareas (IA Generativa con Gemini)

La expansión de ideas en texto libre a tareas estructuradas SÍ requiere comprensión semántica profunda. Para esto se integra **Google Gemini API**.

### ¿Cómo funciona?
1. El usuario envía una descripción natural de su proyecto.
2. El backend inyecta ese texto en un **Prompt de Sistema** cuidadosamente diseñado.
3. Se le ordena a la IA actuar como un Product Owner, forzando la respuesta a retornar estrictamente un formato JSON con 4 a 7 tareas desglosadas.
4. El backend parsea y valida el JSON devuelto antes de insertarlo en la base de datos.

### Sistema de Resiliencia (Fallback)
Las APIs externas son propensas a fallos (Rate Limits, caídas, timeouts). Por eso, el módulo implementa un *Graceful Degradation*:
* **Múltiples Modelos:** El sistema intenta usar `gemini-3.1-flash-lite-preview`, y si falla o no está disponible, cae en cascada a `gemini-2.5-flash` o versiones anteriores.
* **Fallback Interno:** Si Google API está caída, si la API KEY no fue configurada, o si el JSON retornado es inválido, el sistema intercepta el error e inserta **5 tareas genéricas por defecto** que representan el ciclo de vida del software (Planificación, Diseño, etc.). Esto garantiza que la experiencia del usuario nunca se rompa con errores de red.
