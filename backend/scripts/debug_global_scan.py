import asyncio
import logging
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.aws.global_scanner import GlobalResourceScanner
from services.notification_service import NotificationService
from core.config import settings
from services.aws.scanner_registry import ScannerRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_scan_and_report():
    logger.info("1. Initializing Global Scanner...")
    # Initialize with primary region
    scanner = GlobalResourceScanner(region='us-east-1')
    
    # 2. Run Scan
    logger.info("2. Running Global Scan (this might take a few seconds)...")
    # For speed, we will Mock scan_all_regions if it takes too long, 
    # but let's try running it for real or assume the previous session has cached credentials.
    # Actually, let's run it. Alternatively, since this is a debug script, 
    # we can just test the aggregation logic if we had mock data, but integration is better.
    
    # To save time, we can manually patch the regions to just us-east-1 for this test
    # but scan_all_regions calls get_available_regions.
    
    results = await scanner.scan_all_regions()
    
    logger.info(f"3. Scan Results Summary:")
    logger.info(f"   Success: {results.get('success')}")
    logger.info(f"   Total Unused: {results.get('total_resources')}")
    logger.info(f"   Breakdown: {json.dumps(results.get('resource_data', {}), indent=2)}")
    
    if results.get('total_resources', 0) > 0 and results.get('resource_data', {}).get('s3_count', 0) == 0:
        logger.warning("!!! WARNING: Total > 0 but S3/IAM are 0. Aggregation might still be broken if resources exist.")
    
    # 4. Generate Email Content (Dry Run)
    logger.info("4. Generating Email Content...")
    
    template = NotificationService.get_email_template(
        title="[DEBUG] Cloud Cleaner Report",
        content_data=results.get('resource_data', {}),
        scan_summary=f"Found {results.get('total_resources')} unused resources."
    )
    
    # Print a snippet to verify template populated correctly
    logger.info("   Email Template Snippet (Check for counts):")
    for line in template.split('\n'):
        if 'resource-count' in line or 'resource-name' in line:
            print(line.strip())
            
    # 5. Send Real Email if recipients configured (and user wants to verification)
    if settings.notification_email_recipients:
         logger.info(f"5. Sending Email to {settings.notification_email_recipients}...")
         # Uncomment to send
         NotificationService.send_email_notification(
             subject="[DEBUG] Cloud Cleaner Report (Fixed Aggregation)",
             content_data=results['resource_data'],
             recipients=[r.strip() for r in settings.notification_email_recipients.split(',')]
         )
         logger.info("   Email sent.")
    else:
        logger.info("   Skipping email send (no recipients configured).")

if __name__ == "__main__":
    asyncio.run(debug_scan_and_report())
