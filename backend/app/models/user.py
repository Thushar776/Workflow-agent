from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # nullable for Google OAuth users
    full_name = Column(String, nullable=False)
    role = Column(String, default="user")  # "user" or "admin"
    is_active = Column(Boolean, default=True)
    auth_provider = Column(String, default="local")  # "local" or "google"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
