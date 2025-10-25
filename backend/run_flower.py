#!/usr/bin/env python3
"""
Script to run Flower monitoring for Celery tasks
Usage: python run_flower.py
"""
import os
import sys
from core.celery_app import celery_app

if __name__ == "__main__":
    # Import flower after celery_app is initialized
    from flower.command import FlowerCommand
    
    # Get Redis configuration from environment
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    broker_url = f"redis://{redis_host}:{redis_port}/0"
    
    print(f"Starting Flower monitoring...")
    print(f"Broker URL: {broker_url}")
    print(f"Flower will be available at: http://localhost:5555")
    print(f"Press Ctrl+C to stop")
    
    # Run Flower
    flower = FlowerCommand(
        app=celery_app,
        broker=broker_url,
        port=5555,
        address="0.0.0.0"
    )
    
    flower.execute_from_commandline()