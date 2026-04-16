from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.models.user import User
from app.views.schemas import ChatRequest
from app.services.auth import get_current_user
from app.services.chat_service import get_task_status, create_task_id
from app.services.middleware import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("")
async def chat_endpoint(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user)
):
    """Protected chat endpoint — dispatches to Redis queue."""
    task_id = create_task_id(request.message, request.history, current_user.email)
    
    logger.info("chat_job_dispatched", user=current_user.email, task_id=task_id)
    
    return {
        "status": "success",
        "task_id": task_id
    }

@router.get("/status/{task_id}")
def chat_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Poll for task completion."""
    task = get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
