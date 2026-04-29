from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# ─── Instancia principal de FastAPI ───────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Plataforma académica de gestión de proyectos Kanban con IA asistiva.\n\n"
        "**Roles disponibles:** Estudiante, Profesor, Invitado\n\n"
        "Usa el botón **Authorize** con un Bearer token para acceder a endpoints protegidos."
    ),
    version="1.0.0",
    docs_url="/docs",      # Swagger UI — interfaz interactiva
    redoc_url="/redoc",    # ReDoc — documentación alternativa más legible
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Permite que el frontend React (localhost:5173) haga peticiones a este backend.
# En producción, reemplaza allow_origins con tu dominio real.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://192.168.1.7:5173",
],
    allow_credentials=True,    # Necesario para enviar cookies / headers de auth
    allow_methods=["*"],       # GET, POST, PUT, PATCH, DELETE, OPTIONS
    allow_headers=["*"],       # Authorization, Content-Type, etc.
)

# Routers
from app.routers import auth, users, projects, columns, tasks, history, notifications, ai, invitations
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(columns.router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)
app.include_router(history.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai.router, prefix=settings.API_V1_PREFIX)
app.include_router(invitations.router, prefix=settings.API_V1_PREFIX)

# ─── Endpoints base ───────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Verificación de estado")
def root():
    """
    Confirma que la API está activa y retorna información básica.
    Útil para verificar que el servidor arrancó correctamente.
    """
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    """
    Endpoint de salud para monitoreo o Docker health checks.
    Retorna 200 OK si el servidor responde correctamente.
    """
    return {"status": "healthy", "version": "1.0.1 (Roles & Invites)"}

