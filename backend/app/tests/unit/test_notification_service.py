import pytest
from app.schemas.notification import NotificationCreate

def test_notification_create_schema():
    notif_data = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Nueva observación",
        "message": "El profesor ha dejado un comentario.",
        "type": "info"
    }
    notif = NotificationCreate(**notif_data)
    assert notif.title == "Nueva observación"
    assert notif.type == "info"
