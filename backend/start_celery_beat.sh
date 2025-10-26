#!/bin/bash
# Start Celery Beat with RedBeat scheduler

cd "$(dirname "$0")"

echo "Starting Celery Beat with RedBeat scheduler..."
uv run celery -A core.celery_app beat --loglevel=info --scheduler redbeat.RedBeatScheduler