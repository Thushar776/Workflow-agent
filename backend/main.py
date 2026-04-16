from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import uvicorn

from database import init_db, get_db, User
from auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user, require_admin
)
from middleware import RequestTracingMiddleware, logger
from agent import process_message
from encryption import encrypt_pii, decrypt_pii, mask_email
from sqlalchemy.orm import Session

# --- Init ---
app = FastAPI(title="AI Workflow Agent API")
init_db()

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTracingMiddleware)


# ===================== SCHEMAS =====================

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []


# ===================== AUTH ROUTES =====================

@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
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

    # Return tokens immediately (auto-login after registration)
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": _sanitize_user(user),
    }


# --- MFA Cache (In-Memory for Hackathon) ---
import random
OTP_CACHE = {}

@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with email & password. Triggers MFA OTP."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate 6-digit OTP
    otp_code = f"{random.randint(100000, 999999)}"
    OTP_CACHE[req.email] = otp_code
    
    # Mocking Email sent by printing strongly to console
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

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

@app.post("/api/auth/verify-otp")
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Validates the OTP and returns JWT tokens."""
    cached_otp = OTP_CACHE.get(req.email)
    if not cached_otp or cached_otp != req.otp:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Clear OTP
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


@app.post("/api/auth/refresh")
def refresh_token(req: RefreshRequest):
    """Use a refresh token to get a new access token."""
    payload = decode_token(req.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token(data={"sub": payload["sub"], "role": payload.get("role", "user")})
    return {"status": "success", "access_token": new_access}


@app.post("/api/auth/google")
def google_login(request_data: dict, db: Session = Depends(get_db)):
    """
    Simplified Google OAuth handler.
    In production, you'd verify the Google ID token server-side.
    For hackathon: accepts email + name from the frontend Google Sign-In response.
    """
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
        logger.info("google_user_created", email=email)
    else:
        logger.info("google_user_logged_in", email=email)

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})

    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": _sanitize_user(user),
    }


# ===================== PROTECTED ROUTES =====================

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile (sanitized, no PII leak)."""
    return {"status": "success", "user": _sanitize_user(current_user)}


from fastapi import BackgroundTasks
import asyncio
import uuid

# --- Async Task Store ---
TASK_STORE = {}

async def _run_chat_job(task_id: str, message: str, history: list, user_email: str):
    """Background worker function."""
    try:
        logger.info("worker_started", task_id=task_id, user=user_email)
        result = await process_message(message, history)
        TASK_STORE[task_id] = {
            "status": "completed",
            "response": result["response"],
            "history": result["history"],
            "logs": result["logs"]
        }
        logger.info("worker_completed", task_id=task_id)
    except Exception as e:
        logger.error("worker_failed", task_id=task_id, error=str(e))
        TASK_STORE[task_id] = {"status": "error", "detail": str(e)}

@app.post("/api/chat")
async def chat_endpoint(
    request: ChatRequest, 
    background_tasks: BackgroundTasks, 
    current_user: User = Depends(get_current_user)
):
    """Protected chat endpoint — dispatches to async worker."""
    task_id = str(uuid.uuid4())
    TASK_STORE[task_id] = {"status": "processing"}
    
    logger.info("chat_job_dispatched", user=current_user.email, task_id=task_id)
    background_tasks.add_task(_run_chat_job, task_id, request.message, request.history, current_user.email)
    
    return {
        "status": "success",
        "task_id": task_id
    }

@app.get("/api/chat/status/{task_id}")
def chat_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Poll for background task completion."""
    task = TASK_STORE.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ===================== ADMIN ROUTES =====================

@app.get("/api/admin/users")
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Admin-only: list all users (sanitized)."""
    users = db.query(User).all()
    return {"status": "success", "users": [_sanitize_user(u) for u in users]}


# ===================== HELPERS =====================

def _sanitize_user(user: User) -> dict:
    """
    Returns user data without PII (no hashed_password, no raw email in logs).
    This prevents PII from leaking into frontend API responses.
    """
    return {
        "id": user.id,
        "email": mask_email(user.email),
        "full_name": decrypt_pii(user.full_name),
        "role": user.role,
        "auth_provider": user.auth_provider,
    }


# ===================== HEALTH =====================

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "workflow-agent-api"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
