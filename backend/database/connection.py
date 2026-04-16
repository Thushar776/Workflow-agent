from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./workflow_agent.db").strip()

class DatabaseSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls._instance.engine = create_engine(
                DATABASE_URL, 
                connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
            )
            cls._instance.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=cls._instance.engine
            )
            cls._instance.Base = declarative_base()
        return cls._instance

# Exported instance
db_instance = DatabaseSingleton()
Base = db_instance.Base

def get_db():
    db = db_instance.SessionLocal()
    try:
        yield db
    finally:
        db.close()
