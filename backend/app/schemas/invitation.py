import uuid
from pydantic import BaseModel, EmailStr

class InviteSendRequest(BaseModel):
    email: str  # Email del usuario a invitar

class InviteSendResponse(BaseModel):
    message: str

class InvitationAcceptRequest(BaseModel):
    token: str

class InvitationAcceptResponse(BaseModel):
    project_id: uuid.UUID
    project_name: str
    message: str

# Kept for backward compat
class InvitationCreateResponse(BaseModel):
    invitation_link: str
    token: str
