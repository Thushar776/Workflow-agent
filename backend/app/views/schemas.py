from pydantic import BaseModel
from typing import List, Dict, Any, Optional

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

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str
