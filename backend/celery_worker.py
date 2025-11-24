from celery import Celery
import os

# Get Redis connection details from environment variables, with defaults for local dev
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

# Define the Celery application instance
# The broker URL points to Redis. The backend URL also points to Redis
# to store task results.
celery_app = Celery(
    "sadi_worker",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    include=["backend.app.etl_tasks"]  # Auto-discover tasks from this module
)

celery_app.conf.update(
    task_track_started=True,
)

if __name__ == "__main__":
    celery_app.start()
