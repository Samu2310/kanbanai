import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.invitation import (
    InviteSendRequest, InviteSendResponse,
    InvitationAcceptRequest, InvitationAcceptResponse
)
from app.services.invitation_service import (
    send_invitation_by_email,
    accept_invitation,
    decline_invitation
)

router = APIRouter(prefix="", tags=["Invitations"], redirect_slashes=True)


@router.post("/invitations/accept", response_model=InvitationAcceptResponse)
def accept_invitation_endpoint(
    request: InvitationAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acepta una invitación usando el token de la notificación."""
    print(f"DEBUG: Usuario {current_user.email} intentando aceptar invitación con token")
    return accept_invitation(db, request.token, current_user)


@router.post("/invitations/decline", response_model=dict)
def decline_invitation_endpoint(
    request: InvitationAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rechaza una invitación."""
    print(f"DEBUG: Usuario {current_user.email} rechazando invitación")
    return decline_invitation(db, request.token, current_user)
