import uuid
import redis
import json
import os
from app.services.middleware import logger

# Redis Config
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0").strip()
r = redis.from_url(REDIS_URL, decode_responses=True)

TASK_QUEUE = "chat_tasks"

def create_task_id(message: str, history: list, user_email: str):
    """Generates task ID and pushes task to Redis queue."""
    task_id = str(uuid.uuid4())
    
    task_data = {
        "task_id": task_id,
        "message": message,
        "history": history,
        "user_email": user_email
    }
    
    # Set initial status in Redis (expires in 1 hour)
    r.setex(f"task:{task_id}", 3600, json.dumps({"status": "processing"}))
    
    # Atomic push to queue
    r.lpush(TASK_QUEUE, json.dumps(task_data))
    
    return task_id

def get_task_status(task_id: str):
    """Reads task status from Redis."""
    data = r.get(f"task:{task_id}")
    if not data:
        return None
    return json.loads(data)
