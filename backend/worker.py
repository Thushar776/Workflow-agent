import redis
import json
import os
import time
import asyncio
from app.services.agent import process_message
from app.services.middleware import logger

# Redis Config
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0").strip()
r = redis.from_url(REDIS_URL, decode_responses=True)

TASK_QUEUE = "chat_tasks"

async def worker():
    logger.info("background_worker_started", queue=TASK_QUEUE)
    
    while True:
        try:
            # Atomic pop (blocks until a task is available)
            task_raw = r.brpop(TASK_QUEUE, timeout=5)
            if not task_raw:
                continue
            
            # brpop returns (queue_name, data)
            _, data_str = task_raw
            task_data = json.loads(data_str)
            task_id = task_data["task_id"]
            
            # Idempotency Check: Already processed?
            status_raw = r.get(f"task:{task_id}")
            if status_raw:
                status_data = json.loads(status_raw)
                if status_data["status"] == "completed":
                    logger.info("worker_skip_idempotent", task_id=task_id)
                    continue

            logger.info("worker_processing", task_id=task_id, user=task_data["user_email"])
            
            # Execute business logic
            result = await process_message(task_data["message"], task_data["history"])
            
            # Store result back in Redis (atomic update)
            final_data = {
                "status": "completed",
                "response": result["response"],
                "history": result["history"],
                "logs": result["logs"]
            }
            r.setex(f"task:{task_id}", 3600, json.dumps(final_data))
            
            logger.info("worker_success", task_id=task_id)
            
        except Exception as e:
            logger.error("worker_error", error=str(e))
            time.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker())
