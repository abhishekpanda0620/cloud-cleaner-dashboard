import sys
import os
# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.celery_app import celery_app
from redbeat import RedBeatSchedulerEntry
import datetime

try:
    entry = RedBeatSchedulerEntry.from_key(
        'redbeat:scheduled-scan',
        app=celery_app
    )
    print(f"Key: {entry.key}")
    print(f"Schedule: {entry.schedule}")
    print(f"Score (Due At Timestamp): {entry.score}")
    print(f"Due At: {datetime.datetime.fromtimestamp(entry.score)}")
    print(f"Attributes: {dir(entry)}")
except Exception as e:
    print(f"Error: {e}")
