from fastapi import APIRouter, HTTPException
from core.celery_app import celery_app
from celery.result import AsyncResult
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/workers")
async def get_workers():
    """Get information about active Celery workers"""
    try:
        # Get active workers
        inspect = celery_app.control.inspect()
        
        # Get worker stats
        stats = inspect.stats()
        active = inspect.active()
        registered = inspect.registered()
        
        if not stats:
            return {
                "workers": [],
                "total": 0,
                "message": "No active workers found"
            }
        
        workers = []
        for worker_name, worker_stats in stats.items():
            worker_info = {
                "name": worker_name,
                "status": "online",
                "stats": worker_stats,
                "active_tasks": len(active.get(worker_name, [])) if active else 0,
                "registered_tasks": len(registered.get(worker_name, [])) if registered else 0
            }
            workers.append(worker_info)
        
        return {
            "workers": workers,
            "total": len(workers)
        }
        
    except Exception as e:
        logger.error(f"Error fetching worker information: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch worker information: {str(e)}"
        )


@router.get("/tasks/active")
async def get_active_tasks():
    """Get currently active/running tasks"""
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        
        if not active:
            return {
                "tasks": [],
                "total": 0,
                "message": "No active tasks"
            }
        
        all_tasks = []
        for worker_name, tasks in active.items():
            for task in tasks:
                task_info = {
                    "id": task.get('id'),
                    "name": task.get('name'),
                    "worker": worker_name,
                    "args": task.get('args'),
                    "kwargs": task.get('kwargs'),
                    "time_start": task.get('time_start')
                }
                all_tasks.append(task_info)
        
        return {
            "tasks": all_tasks,
            "total": len(all_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error fetching active tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch active tasks: {str(e)}"
        )


@router.get("/tasks/scheduled")
async def get_scheduled_tasks():
    """Get scheduled/reserved tasks"""
    try:
        inspect = celery_app.control.inspect()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        
        all_tasks = []
        
        if scheduled:
            for worker_name, tasks in scheduled.items():
                for task in tasks:
                    task_info = {
                        "id": task.get('request', {}).get('id'),
                        "name": task.get('request', {}).get('name'),
                        "worker": worker_name,
                        "eta": task.get('eta'),
                        "status": "scheduled"
                    }
                    all_tasks.append(task_info)
        
        if reserved:
            for worker_name, tasks in reserved.items():
                for task in tasks:
                    task_info = {
                        "id": task.get('id'),
                        "name": task.get('name'),
                        "worker": worker_name,
                        "status": "reserved"
                    }
                    all_tasks.append(task_info)
        
        return {
            "tasks": all_tasks,
            "total": len(all_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error fetching scheduled tasks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch scheduled tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task by ID"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        task_info = {
            "id": task_id,
            "status": result.status,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None,
            "failed": result.failed() if result.ready() else None,
        }
        
        # Add result or error info if task is complete
        if result.ready():
            if result.successful():
                task_info["result"] = result.result
            elif result.failed():
                task_info["error"] = str(result.info)
        
        return task_info
        
    except Exception as e:
        logger.error(f"Error fetching task status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch task status: {str(e)}"
        )


@router.get("/stats")
async def get_celery_stats():
    """Get overall Celery statistics"""
    try:
        inspect = celery_app.control.inspect()
        
        stats = inspect.stats()
        active = inspect.active()
        scheduled = inspect.scheduled()
        reserved = inspect.reserved()
        registered = inspect.registered()
        
        # Count totals
        total_workers = len(stats) if stats else 0
        total_active = sum(len(tasks) for tasks in active.values()) if active else 0
        total_scheduled = sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0
        total_reserved = sum(len(tasks) for tasks in reserved.values()) if reserved else 0
        
        # Get registered task names
        all_registered_tasks = set()
        if registered:
            for tasks in registered.values():
                all_registered_tasks.update(tasks)
        
        return {
            "workers": {
                "total": total_workers,
                "online": total_workers
            },
            "tasks": {
                "active": total_active,
                "scheduled": total_scheduled,
                "reserved": total_reserved,
                "registered": list(all_registered_tasks)
            },
            "broker": {
                "url": celery_app.conf.broker_url,
                "transport": celery_app.conf.broker_transport
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching Celery stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Celery stats: {str(e)}"
        )


@router.post("/tasks/{task_id}/revoke")
async def revoke_task(task_id: str, terminate: bool = False):
    """Revoke/cancel a task"""
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        
        return {
            "message": f"Task {task_id} revoked successfully",
            "task_id": task_id,
            "terminated": terminate
        }
        
    except Exception as e:
        logger.error(f"Error revoking task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to revoke task: {str(e)}"
        )