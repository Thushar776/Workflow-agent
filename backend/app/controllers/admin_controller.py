from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from app.models.user import User
from app.services.auth import require_admin
from app.services.encryption import mask_email, decrypt_pii

router = APIRouter(prefix="/api/admin", tags=["admin"])

def _sanitize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": mask_email(user.email),
        "full_name": decrypt_pii(user.full_name),
        "role": user.role,
        "auth_provider": user.auth_provider,
    }

@router.get("/users")
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Admin-only: list all users."""
    users = db.query(User).all()
    return {"status": "success", "users": [_sanitize_user(u) for u in users]}
