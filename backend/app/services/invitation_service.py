import uuid
from datetime import timedelta
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.notification import Notification
from app.schemas.invitation import InviteSendResponse, InvitationAcceptResponse
from app.services.project_service import get_project_by_id
from app.core.security import create_access_token, decode_access_token
from app.core.exceptions import BadRequestException, NotFoundException


def send_invitation_by_email(
    db: Session,
    project_id: uuid.UUID,
    target_email: str,
    current_user: User
) -> InviteSendResponse:
    """Envía una invitación a un usuario por email creando una notificación interna."""

    # 1. Verificar que el remitente tiene acceso al proyecto
    project = get_project_by_id(db, project_id, current_user)

    # 2. Buscar al destinatario por email (case-insensitive, sin espacios)
    target_email_clean = target_email.strip().lower()
    print(f"DEBUG: Buscando usuario con email: {repr(target_email_clean)}")
    
    target_user = db.query(User).filter(
        User.email.ilike(target_email_clean)
    ).first()
    
    if not target_user:
        # Debug: list first 5 users to see emails
        all_users = db.query(User.email).limit(5).all()
        print(f"DEBUG: Usuario no encontrado. Usuarios en DB: {all_users}")
        raise NotFoundException(
            f"No se encontró ningún usuario registrado con el correo '{target_email}'. "
            "Asegúrate de que el usuario ya tenga una cuenta en KanbanAI."
        )

    print(f"DEBUG: Usuario encontrado: {target_user.name} (ID: {target_user.id})")

    # 3. No invitarse a sí mismo
    if target_user.id == current_user.id:
        raise BadRequestException("No puedes invitarte a ti mismo.")

    # 4. Verificar que el destinatario no es ya miembro
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == target_user.id
    ).first()
    if existing:
        raise BadRequestException(f"{target_email} ya es miembro de este proyecto.")

    # 5. Verificar si ya hay una invitación pendiente (notificación no leída)
    existing_invite = db.query(Notification).filter(
        Notification.user_id == target_user.id,
        Notification.type == "project_invite",
        Notification.is_read == False
    ).join(Project, Project.id == project_id).first()
    # Simple check: look for any existing invite for this project
    existing_invite = db.query(Notification).filter(
        Notification.user_id == target_user.id,
        Notification.type == "project_invite",
        Notification.is_read == False,
        Notification.invitation_token.isnot(None)
    ).all()

    # Check if any of these have a token for this project
    for notif in existing_invite:
        payload = decode_access_token(notif.invitation_token)
        if payload and payload.get("type") == "invitation" and payload.get("sub") == str(project_id):
            raise BadRequestException(f"Ya existe una invitación pendiente para {target_email}.")

    # 6. Generar token JWT para la invitación (7 días)
    token_data = {"sub": str(project_id), "type": "invitation"}
    token = create_access_token(data=token_data, expires_delta=timedelta(days=7))

    # 7. Crear notificación interna para el destinatario
    notification = Notification(
        user_id=target_user.id,
        type="project_invite",
        title=f"Invitación al proyecto: {project.name}",
        message=f"{current_user.name} te ha invitado a colaborar en el proyecto '{project.name}'.",
        invitation_token=token
    )
    db.add(notification)
    db.commit()

    return InviteSendResponse(message=f"Invitación enviada a {target_email} exitosamente.")


def accept_invitation(db: Session, token: str, current_user: User) -> InvitationAcceptResponse:
    """Acepta una invitación usando el token embebido en la notificación."""
    try:
        payload = decode_access_token(token)
        if not payload or payload.get("type") != "invitation":
            print(f"DEBUG: Token inválido. Payload: {payload}")
            raise BadRequestException("Token de invitación inválido o expirado.")

        project_id_str = payload.get("sub")
        print(f"DEBUG: Aceptando invitación para proyecto ID: {project_id_str}")
        
        if not project_id_str:
            raise BadRequestException("Token mal formado.")

        try:
            project_id = uuid.UUID(project_id_str)
        except ValueError:
            raise BadRequestException("ID de proyecto inválido.")

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            print(f"DEBUG: Proyecto {project_id} no existe")
            raise BadRequestException("El proyecto no existe.")

        # Check if already a member
        existing_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()

        if not existing_member:
            print(f"DEBUG: Añadiendo usuario {current_user.email} al proyecto {project.name}")
            # Add as member
            new_member = ProjectMember(
                project_id=project_id,
                user_id=current_user.id,
                role_in_project=ProjectMemberRole.member
            )
            db.add(new_member)

        # Mark the invitation notification as read
        db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.type == "project_invite",
            Notification.invitation_token == token
        ).update({"is_read": True})

        db.commit()
        print(f"DEBUG: Invitación aceptada con éxito por {current_user.email}")

        return InvitationAcceptResponse(
            project_id=project.id,
            project_name=project.name,
            message="Te has unido al proyecto exitosamente."
        )
    except Exception as e:
        print(f"ERROR en accept_invitation: {str(e)}")
        db.rollback()
        raise e


def decline_invitation(db: Session, token: str, current_user: User) -> dict:
    """Rechaza una invitación marcando la notificación como leída."""
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "invitation":
        raise BadRequestException("Token de invitación inválido o expirado.")

    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.type == "project_invite",
        Notification.invitation_token == token
    ).update({"is_read": True})
    db.commit()

    return {"message": "Invitación rechazada."}
