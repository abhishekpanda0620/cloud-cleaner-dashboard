import sys
import os
import requests
import redis
from time import sleep

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.config import settings
    REDIS_HOST = settings.redis_host
    REDIS_PORT = settings.redis_port
    API_URL = f"http://{settings.host}:{settings.port}"
except ImportError:
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    API_URL = "http://localhost:8000"

def clear_redis():
    print(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        r.flushall()
        print("✅ Redis cache flushed successfully.")
    except Exception as e:
        print(f"❌ Failed to flush Redis: {e}")

def clear_app_cache():
    print(f"Clearing application in-memory cache via API at {API_URL}...")
    try:
        # We need to implement this endpoint first!
        response = requests.post(f"{API_URL}/api/admin/clear-cache", timeout=10)
        if response.status_code == 200:
            print("✅ Application cache cleared successfully.")
        else:
            print(f"⚠️ API returned {response.status_code}: {response.text}")
            print("   (Note: You might need to add the /api/admin/clear-cache endpoint)")
    except Exception as e:
        print(f"❌ Failed to contact API: {e}")

if __name__ == "__main__":
    print("--- Cloud Cleaner Cache Clearing Tool ---")
    clear_redis()
    clear_app_cache()
    print("-----------------------------------------")
