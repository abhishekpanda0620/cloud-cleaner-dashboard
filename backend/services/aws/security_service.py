import logging
import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.security import SecurityFinding, FindingStatus
from services.aws.security import IAMSecurityScanner, CloudTrailSecurityScanner, S3SecurityScanner, EC2SecurityScanner, MonitoringSecurityScanner

logger = logging.getLogger(__name__)

class SecurityService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def run_all_scanners(self) -> List[Dict[str, Any]]:
        """
        Run all registered security scanners and save results.
        """
        logger.info("Starting security scan...")
        
        # Instantiate scanners
        # Note: Scanners instantiate their own Boto3 sessions.
        scanners = [
            IAMSecurityScanner(),
            CloudTrailSecurityScanner(region='us-east-1'), 
            S3SecurityScanner(region='us-east-1'),
            EC2SecurityScanner(region='us-east-1'),
            MonitoringSecurityScanner(region='us-east-1')
        ]

        total_findings = []

        for scanner in scanners:
            try:
                logger.info(f"Running {scanner.service_name} security scanner...")
                # run_checks is synchronous, but that's fine for now as it makes API calls
                # blocking the loop isn't ideal but acceptable for this stage or run in threadpool
                findings = scanner.run_checks() 
                total_findings.extend(findings)
                logger.info(f"Scanned {scanner.service_name}: {len(findings)} findings")
            except Exception as e:
                logger.error(f"Failed to run {scanner.service_name} scanner: {e}")

        # Save to Database
        if total_findings:
            await self.save_findings(total_findings)
        
        return total_findings

    async def save_findings(self, findings_data: List[Dict[str, Any]]):
        """
        Upsert findings into the database.
        """
        for data in findings_data:
            check_id = data['check_id']
            resource_id = data['resource_id']
            
            # Check if finding exists
            stmt = select(SecurityFinding).where(
                SecurityFinding.check_id == check_id,
                SecurityFinding.resource_id == resource_id
            )
            result = await self.session.execute(stmt)
            existing_finding = result.scalars().first()

            if existing_finding:
                # Update existing
                existing_finding.status = data['status']
                existing_finding.evidence = data['evidence']
                existing_finding.last_updated_at = datetime.datetime.utcnow()
                # Also update metadata if changed
                existing_finding.resource_type = data['resource_type']
                existing_finding.region = data['region']
                existing_finding.account_id = data['account_id']
                
                await self.session.flush()
            else:
                # Create new
                new_finding = SecurityFinding(
                    check_id=check_id,
                    resource_id=resource_id,
                    resource_type=data['resource_type'],
                    account_id=data['account_id'],
                    region=data['region'],
                    status=data['status'],
                    evidence=data['evidence']
                )
                self.session.add(new_finding)
        
        await self.session.commit()
        logger.info(f"Saved {len(findings_data)} findings to database.")
