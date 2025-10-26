from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from core.cache import get_redis_client
from core.celery_app import celery_app
from redbeat import RedBeatSchedulerEntry
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ScheduleConfig(BaseModel):
    """Schedule configuration model"""
    enabled: bool
    frequency: str  # 'hourly', 'daily', 'weekly', 'custom'
    channels: List[str]  # ['slack', 'email']
    custom_interval: Optional[int] = None  # Minutes for custom frequency


class ScheduleStatus(BaseModel):
    """Schedule status model"""
    enabled: bool
    frequency: str
    channels: List[str]
    last_scan: Optional[str] = None
    next_scan: Optional[str] = None


def get_interval_from_frequency(frequency: str, custom_interval: Optional[int] = None) -> timedelta:
    """Convert frequency string to timedelta interval"""
    if frequency == 'hourly':
        return timedelta(hours=1)
    elif frequency == 'daily':
        return timedelta(days=1)
    elif frequency == 'weekly':
        return timedelta(weeks=1)
    elif frequency == 'custom' and custom_interval:
        return timedelta(minutes=custom_interval)
    else:
        raise ValueError(f"Invalid frequency: {frequency}")


def update_schedule(enabled: bool, frequency: str, custom_interval: Optional[int] = None):
    """Update or remove the scheduled task in RedBeat"""
    try:
        entry_name = 'scheduled-scan'
        
        if enabled:
            # Calculate interval
            interval = get_interval_from_frequency(frequency, custom_interval)
            
            # Create or update the schedule entry
            entry = RedBeatSchedulerEntry(
                entry_name,
                'core.tasks.scheduled_scan_task',
                schedule=interval,
                app=celery_app
            )
            entry.save()
            logger.info(f"Schedule updated: {frequency} ({interval})")
        else:
            # Remove the schedule entry
            try:
                entry = RedBeatSchedulerEntry.from_key(
                    f'redbeat:{entry_name}',
                    app=celery_app
                )
                entry.delete()
                logger.info("Schedule disabled and removed")
            except KeyError:
                logger.info("No existing schedule to remove")
                
    except Exception as e:
        logger.error(f"Error updating schedule: {str(e)}")
        raise


@router.get("/config", response_model=ScheduleConfig)
async def get_schedule_config():
    """Get current schedule configuration"""
    try:
        redis_client = get_redis_client()
        
        # Get configuration from Redis
        enabled = redis_client.get('schedule:enabled')
        frequency = redis_client.get('schedule:frequency')
        channels = redis_client.get('schedule:channels')
        custom_interval = redis_client.get('schedule:custom_interval')
        
        return {
            'enabled': enabled.decode('utf-8') == 'true' if enabled else False,
            'frequency': frequency.decode('utf-8') if frequency else 'daily',
            'channels': channels.decode('utf-8').split(',') if channels else [],
            'custom_interval': int(custom_interval.decode('utf-8')) if custom_interval else None
        }
        
    except Exception as e:
        logger.error(f"Error getting schedule config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_schedule_config(config: ScheduleConfig):
    """Update schedule configuration"""
    try:
        redis_client = get_redis_client()
        
        # Validate channels
        valid_channels = {'slack', 'email'}
        if not all(ch in valid_channels for ch in config.channels):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid channels. Must be one or more of: {valid_channels}"
            )
        
        # Validate frequency
        valid_frequencies = {'hourly', 'daily', 'weekly', 'custom'}
        if config.frequency not in valid_frequencies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid frequency. Must be one of: {valid_frequencies}"
            )
        
        # Validate custom interval
        if config.frequency == 'custom' and not config.custom_interval:
            raise HTTPException(
                status_code=400,
                detail="custom_interval is required when frequency is 'custom'"
            )
        
        # Store configuration in Redis
        redis_client.set('schedule:enabled', 'true' if config.enabled else 'false')
        redis_client.set('schedule:frequency', config.frequency)
        redis_client.set('schedule:channels', ','.join(config.channels))
        if config.custom_interval:
            redis_client.set('schedule:custom_interval', str(config.custom_interval))
        
        # Update Celery Beat schedule
        update_schedule(config.enabled, config.frequency, config.custom_interval)
        
        logger.info(f"Schedule config updated: enabled={config.enabled}, frequency={config.frequency}, channels={config.channels}")
        
        return {
            'message': 'Schedule configuration updated successfully',
            'config': config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating schedule config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=ScheduleStatus)
async def get_schedule_status():
    """Get schedule status including last and next scan times"""
    try:
        redis_client = get_redis_client()
        
        # Get configuration
        enabled = redis_client.get('schedule:enabled')
        frequency = redis_client.get('schedule:frequency')
        channels = redis_client.get('schedule:channels')
        last_scan = redis_client.get('schedule:last_scan')
        custom_interval = redis_client.get('schedule:custom_interval')
        
        # Get next scan time from RedBeat
        next_scan = None
        if enabled and enabled.decode('utf-8') == 'true':
            try:
                entry = RedBeatSchedulerEntry.from_key(
                    'redbeat:scheduled-scan',
                    app=celery_app
                )
                # Calculate next run time
                if entry.schedule:
                    last_run = datetime.fromisoformat(last_scan.decode('utf-8')) if last_scan else datetime.now()
                    freq = frequency.decode('utf-8') if frequency else 'daily'
                    custom_int = int(custom_interval.decode('utf-8')) if custom_interval else None
                    interval = get_interval_from_frequency(freq, custom_int)
                    next_scan = (last_run + interval).isoformat()
            except KeyError:
                logger.warning("Schedule entry not found in RedBeat")
            except Exception as e:
                logger.error(f"Error calculating next scan time: {str(e)}")
        
        return {
            'enabled': enabled.decode('utf-8') == 'true' if enabled else False,
            'frequency': frequency.decode('utf-8') if frequency else 'daily',
            'channels': channels.decode('utf-8').split(',') if channels else [],
            'last_scan': last_scan.decode('utf-8') if last_scan else None,
            'next_scan': next_scan
        }
        
    except Exception as e:
        logger.error(f"Error getting schedule status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable")
async def enable_schedule():
    """Enable scheduled scans"""
    try:
        redis_client = get_redis_client()
        
        # Get current frequency
        frequency = redis_client.get('schedule:frequency')
        custom_interval = redis_client.get('schedule:custom_interval')
        
        if not frequency:
            # Set default frequency if not configured
            frequency = b'daily'
            redis_client.set('schedule:frequency', 'daily')
        
        # Enable schedule
        redis_client.set('schedule:enabled', 'true')
        
        # Update Celery Beat schedule
        update_schedule(
            True,
            frequency.decode('utf-8'),
            int(custom_interval.decode('utf-8')) if custom_interval else None
        )
        
        logger.info("Scheduled scans enabled")
        
        return {
            'message': 'Scheduled scans enabled successfully',
            'enabled': True
        }
        
    except Exception as e:
        logger.error(f"Error enabling schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/disable")
async def disable_schedule():
    """Disable scheduled scans"""
    try:
        redis_client = get_redis_client()
        
        # Disable schedule
        redis_client.set('schedule:enabled', 'false')
        
        # Remove from Celery Beat
        update_schedule(False, 'daily')
        
        logger.info("Scheduled scans disabled")
        
        return {
            'message': 'Scheduled scans disabled successfully',
            'enabled': False
        }
        
    except Exception as e:
        logger.error(f"Error disabling schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger")
async def trigger_scan_now():
    """Manually trigger a scan immediately"""
    try:
        from core.tasks import scheduled_scan_task
        
        # Trigger the task asynchronously
        task = scheduled_scan_task.apply_async()
        
        logger.info(f"Manual scan triggered with task ID: {task.id}")
        
        return {
            'message': 'Scan triggered successfully',
            'task_id': task.id
        }
        
    except Exception as e:
        logger.error(f"Error triggering scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))