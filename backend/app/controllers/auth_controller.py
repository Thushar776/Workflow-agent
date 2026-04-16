from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from app.models.user import User
from app.views.schemas import RegisterRequest, LoginRequest, RefreshRequest, VerifyOTPRequest
from app.services.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user
)
from app.services.encryption import encrypt_pii, decrypt_pii, mask_email
from app.services.middleware import logger
import random

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- MFA Cache (In-Memory for Hackathon) ---
OTP_CACHE = {}

def _sanitize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": mask_email(user.email),
        "full_name": decrypt_pii(user.full_name),
        "role": user.role,
        "auth_provider": user.auth_provider,
    }

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=encrypt_pii(req.full_name),
        role="user",
        auth_provider="local",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("user_registered", email=req.email, role="user")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": _sanitize_user(user),
    }

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    otp_code = f"{random.randint(100000, 999999)}"
    OTP_CACHE[req.email] = otp_code
    
    print("\n" + "="*40)
    print(f"📧 EMAIL SENT TO: {req.email}")
    print(f"🔐 YOUR MFA OTP CODE IS: {otp_code}")
    print("="*40 + "\n")

    logger.info("mfa_otp_generated", email=req.email)

    return {
        "status": "mfa_required",
        "email": req.email,
        "message": "Please enter the OTP sent to your email."
    }

@router.post("/verify-otp")
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    cached_otp = OTP_CACHE.get(req.email)
    if not cached_otp or cached_otp != req.otp:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    del OTP_CACHE[req.email]
    logger.info("user_logged_in_mfa_success", email=req.email)

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": _sanitize_user(user),
    }

@router.post("/refresh")
def refresh_token(req: RefreshRequest):
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token(data={"sub": payload["sub"], "role": payload.get("role", "user")})
    return {"status": "success", "access_token": new_access}

@router.post("/google")
def google_login(request_data: dict, db: Session = Depends(get_db)):
    email = request_data.get("email")
    name = request_data.get("name", "Google User")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=encrypt_pii(name),
            role="user",
            auth_provider="google",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": _sanitize_user(user),
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"status": "success", "user": _sanitize_user(current_user)}
