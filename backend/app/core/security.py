from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# ─── Contexto de hashing ───────────────────────────────────────────────────────
# bcrypt es el algoritmo recomendado para contraseñas.
# "deprecated=auto" actualiza automáticamente hashes antiguos al verificar.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Convierte una contraseña en texto plano a su hash bcrypt.
    
    Ejemplo:
        hash_password("mi_clave_123") → "$2b$12$..."
    
    NUNCA almacenar contraseñas en texto plano.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con su hash bcrypt.
    
    Retorna True si coincide, False si no.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JWT (JSON Web Token) firmado con la SECRET_KEY.
    
    Parámetros:
        data: Payload del token. Incluirá al menos {"sub": user_id}.
        expires_delta: Duración personalizada. Si es None, usa ACCESS_TOKEN_EXPIRE_MINUTES.
    
    Retorna el token como string. Se envía al frontend para autenticar requests.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT.
    
    Retorna el payload (dict) si el token es válido y no expiró.
    Retorna None si el token es inválido, expiró o fue manipulado.
    
    El payload contendrá campos como:
        {"sub": "user-uuid", "role": "student", "exp": 1234567890}
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
