from celery import Celery
from core.config import settings
from redbeat import RedBeatSchedulerEntry
from datetime import timedelta

# Create Celery instance
celery_app = Celery(
    "cloud_cleaner",
    broker=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    backend=f"redis://{settings.redis_host}:{settings.redis_port}/0",
    include=["core.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # RedBeat configuration
    redbeat_redis_url=f"redis://{settings.redis_host}:{settings.redis_port}/1",
    beat_max_loop_interval=5,  # Check for schedule changes every 5 seconds
)