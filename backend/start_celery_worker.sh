#!/bin/bash
# Script to start Celery worker with uv

echo "Starting Celery worker..."
echo "Make sure Redis is running: redis-server"
echo ""

# Change to backend directory
cd "$(dirname "$0")"

# Run celery worker using uv
uv run python -m celery -A core.celery_app worker --loglevel=info