from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

import os

class Settings(BaseSettings):
    """
    Configuración central de la aplicación.
    Los valores se leen automáticamente desde el archivo .env
    gracias a pydantic-settings.
    """

    # ─── Base de datos ─────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://kanbanai:kanbanai_pass@db:5432/kanbanai_db"
)
    

    # ─── JWT ───────────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas

    # ─── Aplicación ────────────────────────────────────────────────
    PROJECT_NAME: str = "KanbanAI"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # ─── IA (Gemini) ────────────────────────────────────────────────
    # Coloca tu clave de la API de Google en el archivo .env:
    # GEMINI_API_KEY=tu_clave_aqui
    # Si no se define, la IA usará el motor heurístico local como fallback.
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


    # pydantic-settings v2: configuración mediante model_config
    # env_file   → lee variables desde el archivo .env
    # extra      → "ignore" permite que haya variables en .env que no estén
    #              declaradas aquí (ej: POSTGRES_* que solo usa Docker Compose)
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna la instancia de Settings cacheada.
    @lru_cache() garantiza que el .env se lee solo una vez,
    no en cada request.
    """
    return Settings()


# Instancia global para importar directamente en otros módulos
settings = get_settings()
