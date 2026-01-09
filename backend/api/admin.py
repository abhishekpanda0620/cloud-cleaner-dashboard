from fastapi import APIRouter, Depends, HTTPException
from core.cache import get_cache
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/clear-cache")
async def clear_cache_endpoint():
    """
    Clear the application's in-memory cache.
    Useful for forcing a refresh of cached data like regions or IAM policies.
    """
    try:
        cache = get_cache()
        cache.clear()
        logger.info("Manual cache clear requested via API")
        return {"status": "success", "message": "In-memory cache cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
