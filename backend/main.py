import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import db_instance
from app.controllers import auth_controller, chat_controller, admin_controller
from app.services.middleware import RequestTracingMiddleware

app = FastAPI(title="AI Workflow Agent API - MVC")

# --- Init DB ---
db_instance.Base.metadata.create_all(bind=db_instance.engine)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTracingMiddleware)

# --- Routers ---
app.include_router(auth_controller.router)
app.include_router(chat_controller.router)
app.include_router(admin_controller.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "workflow-agent-mvc"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
