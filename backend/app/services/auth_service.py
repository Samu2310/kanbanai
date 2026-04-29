from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User
from app.schemas.user import UserCreate, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import ConflictException, UnauthorizedException

def register_user(db: Session, user_in: UserCreate) -> User:
    """Registra un nuevo usuario en el sistema."""
    hashed_pwd = hash_password(user_in.password)
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_pwd,
        role=user_in.role
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ConflictException("El correo electrónico ya está registrado.")

def authenticate_user(db: Session, form_data: OAuth2PasswordRequestForm) -> Token:
    """Valida credenciales y retorna un token JWT."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedException("Correo electrónico o contraseña incorrectos.")
    
    if not user.is_active:
        raise UnauthorizedException("El usuario está inactivo.")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    return Token(access_token=access_token, token_type="bearer")
