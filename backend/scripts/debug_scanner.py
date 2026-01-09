import sys
import os
import asyncio
import logging

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.aws.scanners.ec2_scanner import EC2Scanner
from core.config import settings

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_scanner():
    print("Initializing EC2 Scanner...")
    try:
        scanner = EC2Scanner()
        
        print(f"Supported Regions: {scanner.get_supported_regions()}")
        
        print("Starting Scan...")
        resources = scanner.scan()
        
        print(f"Scan Complete. Found {len(resources)} resources.")
        for r in resources:
            print(f"- [{r['resource_type']}] {r['resource_id']} ({r['region']})")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ensure we can run async code if needed, but scanner.scan is synchronous
    debug_scanner()
