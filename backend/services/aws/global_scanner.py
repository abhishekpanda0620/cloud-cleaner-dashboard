import logging
import asyncio
from typing import Dict, Any, List
from core.aws_client import AWSClient
from services.aws.scanner_registry import ScannerRegistry

logger = logging.getLogger(__name__)

class GlobalResourceScanner:
    def __init__(self, region: str = 'us-east-1'):
        self.primary_region = region
        self.scanner_registry = ScannerRegistry()

    async def scan_all_regions(self) -> Dict[str, Any]:
        """
        Scans all enabled regions for resources using registered scanners.
        """
        aws_client = AWSClient()
        regions = aws_client.get_available_regions()
        logger.info(f"Starting global scan across {len(regions)} regions")

        all_results = []
        
        # Parallel scan across regions
        # Chunking to avoid rate limits if necessary, but starting with full parallel for speed
        tasks = [self._scan_region(region) for region in regions]
        region_results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_scans = 0
        total_unused_count = 0
        
        # Aggregated stats
        ec2_count = 0
        ebs_count = 0
        s3_count = 0
        iam_users_count = 0
        access_keys_count = 0
        high_risk_keys = 0
        
        detailed_breakdown = {}

        for res in region_results:
            if isinstance(res, Exception):
                logger.error(f"Region scan failed: {res}")
                continue
                
            if res:
                successful_scans += 1
                total_unused_count += res.get('unused_count', 0)
                
                # Aggregate specific counts
                region_name = res.get('region')
                data = res.get('data', {})
                
                # EC2
                r_ec2 = data.get('AmazonEC2', [])
                ec2_count += len(r_ec2)
                
                # EBS
                r_ebs = data.get('EC2Other', []) # EBS is usually under EC2Other or specific EBS scanner
                # Note: EC2OtherScanner covers EBS snapshots + EIPs. 
                # EBS Volumes might be under AmazonEC2 if the scanner handles it, or EC2Other.
                # Inspecting EC2Scanner/EC2OtherScanner output would be ideal.
                # Assuming 'EC2Other' captures snapshots/EIPs. 
                ebs_count += len(r_ebs)
                
                # S3
                r_s3 = data.get('AmazonS3', [])
                s3_count += len(r_s3)
                
                # IAM (Users)
                r_iam = data.get('IAMUser', [])
                iam_users_count += len(r_iam)
                
                # Access Keys (Usually returned by IAM scanner as separate items or sub-items)
                # For this implementation, we might not separate them cleanly without more logic.
                # Assuming 'IAMUser' dicts might have 'issues' related to keys.
                
                # Security logic for high risk keys
                # Simplify: access keys count is number of users with key issues
                access_keys_count = 0 # Difficult to separate without deep inspection
                
                # Count high risk keys (e.g., in IAMUser findings)
                for user in r_iam:
                    # check issues for 'Access Key'
                    for issue in user.get('issues', []):
                         if 'Access Key' in issue:
                             access_keys_count += 1
                             if 'unused for' in issue:
                                 # Parse days? Assuming any unused key > 90 days.
                                 # The text is "Access Key X unused for N days"
                                 try:
                                     parts = issue.split()
                                     days_idx = parts.index('days')
                                     days = int(parts[days_idx-1])
                                     if days > 90:
                                         high_risk_keys += 1
                                 except: pass

        logger.info(f"Global scan complete. Unused resources: {total_unused_count}")

        return {
            'success': True,
            'regions_scanned': successful_scans,
            'total_resources': total_unused_count,
            'resource_data': {
                'ec2_count': ec2_count,
                'ebs_count': ebs_count,
                's3_count': s3_count,
                'iam_users_count': iam_users_count,
                'access_keys_count': access_keys_count,
                'high_risk_keys': high_risk_keys,
                'rds_count': 0, # Add if needed, e.g. data.get('AmazonRDS', [])
                'lambda_count': 0 # Add if needed
            }
        }

    async def _scan_region(self, region: str) -> Dict[str, Any]:
        """
        Scans a single region for all registered resource types.
        """
        try:
            scanners = self.scanner_registry.get_scanners()
            region_data = {}
            unused_count = 0
            
            # 1. Run Standard Scanners (EC2, S3, RDS, etc.)
            for service_code, scanner_cls in scanners.items():
                # Skip global services if not in primary region to avoid duplicate calls
                is_global = service_code in ['AmazonS3', 'AWSLambda', 'AmazonRoute53'] # Simplified logic
                if is_global and region != 'us-east-1':
                    continue

                try:
                    # Instantiate and run scanner
                    scanner = scanner_cls(region=region)
                    # Run blocking scan in thread pool
                    resources = await asyncio.to_thread(scanner.scan)
                    
                    unused_items = [r for r in resources if r.get('status') == 'unused']
                    
                    # Store by service code (e.g., 'AmazonEC2')
                    region_data[service_code] = unused_items
                    unused_count += len(unused_items)
                    
                except Exception as e:
                    logger.warning(f"Scanner {service_code} failed in {region}: {e}")

            # 2. Run Security Scanners (IAM) - Only in primary region
            if region == 'us-east-1':
                from services.aws.security.iam_scanner import IAMSecurityScanner
                try:
                    iam_scanner = IAMSecurityScanner(region=region)
                    exclude_checks = ['check_iam_root_keys', 'check_iam_root_mfa', 'check_iam_password_policy']
                    
                    # IAM Scanner returns findings, we need to extract resources
                    # For this report, 'unused' usually corresponds to check_iam_unused_creds
                    findings = await asyncio.to_thread(iam_scanner.run_checks)
                    
                    iam_users_unused = []
                    
                    for f in findings:
                        if f['check_id'] == 'check_iam_unused_creds' and f['status'] == 'FAIL':
                            # Extract user details from evidence
                            evidence = f.get('evidence', {})
                            details = evidence.get('details', [])
                            for u in details:
                                iam_users_unused.append({'user': u['user'], 'issues': u['issues']})
                    
                    if iam_users_unused:
                        region_data['IAMUser'] = iam_users_unused
                        unused_count += len(iam_users_unused)
                        
                except Exception as e:
                    logger.warning(f"IAM Scanner failed: {e}")

            return {
                'region': region,
                'unused_count': unused_count,
                'data': region_data
            }

        except Exception as e:
            logger.error(f"Error scanning region {region}: {str(e)}")
            raise
