"""
Archivo de entorno de Alembic.

Este script se ejecuta cada vez que corres un comando alembic (migrate, upgrade, etc.).
Su responsabilidad es configurar la conexión a la BD y apuntar a los modelos
para que Alembic pueda generar migraciones automáticas comparando el estado
actual de la BD con los modelos SQLAlchemy.
"""
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ─── Añadir el directorio backend/ al path de Python ─────────────────────────
# Esto permite que alembic importe los módulos de app/ aunque se ejecute
# desde el directorio backend/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Importar configuración y Base ────────────────────────────────────────────
from app.config import settings
from app.database import Base

# ─── Importar TODOS los modelos aquí ──────────────────────────────────────────
# Al importar app.models, su __init__.py registra automáticamente todos los
# modelos en Base.metadata en el orden correcto de dependencias.
import app.models  # noqa: F401

# ─── Configuración de Alembic ─────────────────────────────────────────────────
config = context.config

# Inyectar la DATABASE_URL desde nuestra config (lee del .env)
# Esto sobrescribe cualquier sqlalchemy.url en alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de los modelos — Alembic la usará para generar migraciones
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Modo offline: genera el SQL de migración sin conectarse a la BD.
    Útil para revisar el SQL antes de ejecutarlo o para entornos
    donde no hay conexión disponible al momento de generar la migración.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Modo online: se conecta a la BD y ejecuta las migraciones directamente.
    Este es el modo que se usa normalmente con `alembic upgrade head`.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Sin pool en migraciones (conexión única)
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# ─── Punto de entrada ─────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
