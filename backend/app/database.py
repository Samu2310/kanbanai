from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


# ─── Motor de base de datos ────────────────────────────────────────────────────
# pool_pre_ping=True: antes de cada uso, SQLAlchemy verifica que la conexión
# siga activa. Evita errores si PostgreSQL reinicia el contenedor Docker.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# ─── Fábrica de sesiones ───────────────────────────────────────────────────────
# autocommit=False → los cambios no se guardan hasta hacer db.commit()
# autoflush=False  → no se sincroniza con BD hasta hacer db.flush() explícito
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Clase Base para modelos ───────────────────────────────────────────────────
# Todos los modelos SQLAlchemy heredarán de esta clase Base.
# DeclarativeBase es la forma moderna de SQLAlchemy 2.x.
class Base(DeclarativeBase):
    pass


# ─── Dependency de FastAPI ─────────────────────────────────────────────────────
def get_db():
    """
    Generador que provee una sesión de BD por cada request HTTP.
    
    Uso en routers:
        @router.get("/ejemplo")
        def mi_endpoint(db: Session = Depends(get_db)):
            ...
    
    La sesión se cierra automáticamente al terminar el request,
    incluso si ocurre una excepción (gracias al bloque finally).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
