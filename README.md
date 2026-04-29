# 🎯 KanbanAI - Gestor Ágil Inteligente

Bienvenido a **KanbanAI**, una plataforma académica diseñada para facilitar la gestión de proyectos de desarrollo de software integrando herramientas de Inteligencia Artificial y dinámicas metodológicas ágiles.

## 🧠 ¿Qué es KanbanAI?
KanbanAI es un tablero Kanban colaborativo vitaminado. A diferencia de un Trello o Jira tradicional, KanbanAI incluye dos superpoderes:
1. **Generación de Tareas Asistida:** Convierte una simple descripción de proyecto en historias de usuario/tareas utilizando Google Gemini.
2. **Scrum Master Virtual:** Analiza constantemente el flujo de trabajo de tu equipo utilizando un motor heurístico de alta velocidad para detectar tareas vencidas, personas sobrecargadas, cuellos de botella y violaciones a límites WIP, proporcionándote alertas en tiempo real.

## 🛠️ Stack Tecnológico
* **Frontend:** React.js, Vite, TailwindCSS
* **Backend:** Python, FastAPI, SQLAlchemy, Alembic
* **Base de Datos:** PostgreSQL
* **Infraestructura:** Docker & Docker Compose
* **Inteligencia:** Motor Heurístico Propio + Google Gemini API

## 🚀 Cómo correr el proyecto (Quickstart)

El proyecto está completamente dockerizado. Solo necesitas Docker Desktop instalado.

1. **Clona o descarga el repositorio.**
2. **Abre una terminal en la raíz del proyecto.**
3. **Levanta los contenedores:**
   ```bash
   docker-compose up --build
   ```
4. **Ejecuta las migraciones de la base de datos (En otra terminal):**
   ```bash
   docker exec kanbanai_backend alembic upgrade head
   ```
5. **Accede a la aplicación:** Abre tu navegador en `http://localhost:5173`

> **Nota para exposiciones:** Si deseas acceder desde tu teléfono móvil u otro PC en la red, consulta la [Guía de Despliegue en LAN (DEPLOY.md)](./DEPLOY.md).

## 📚 Documentación

En la carpeta [`/docs`](./docs) encontrarás toda la documentación técnica y académica:
* 🏛️ [Arquitectura del Sistema](./docs/arquitectura.md)
* 📖 [Manual de Usuario](./docs/manual_usuario.md)
* ⚙️ [Manual Técnico](./docs/manual_tecnico.md)
* 🤖 [Uso de Inteligencia Artificial](./docs/uso_ia.md)
* ✅ [Reporte de Pruebas](./docs/pruebas.md)

---
*Proyecto académico desarrollado para la asignatura Electiva IA.*
*Equipo:* [Tu Nombre Aquí]
