from typing import List, Dict, Any
import logging
from .base import SecurityScannerBase
from models.security import FindingStatus

logger = logging.getLogger(__name__)

class CloudTrailSecurityScanner(SecurityScannerBase):
    
    @property
    def service_name(self) -> str:
        return "CloudTrail"

    def run_checks(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            # CloudTrail is region-specific, but trails can be multi-region.
            # Best practice: Check describe_trails in current region, see if MultiRegionTrail is enabled.
            # For simplicity in MVP, we scan in the current region.
            ct_client = self.session.client('cloudtrail', region_name=self.region)
            
            
            # CIS 2.1 Ensure CloudTrail is enabled in all regions
            findings.append(self._check_cloudtrail_enabled(ct_client))
            
            # CIS 2.2 Ensure CloudTrail log file validation is enabled
            findings.extend(self._check_log_file_validation(ct_client))

        except Exception as e:
            logger.error(f"Error running CloudTrail security checks: {e}")
            
        return [f for f in findings if f] # Filter None

    def _check_cloudtrail_enabled(self, client) -> Dict[str, Any]:
        """
        CIS 2.1: Ensure CloudTrail is enabled in all regions.
        """
        try:
            response = client.describe_trails()
            trails = response.get('trailList', [])
            
            # Logic: At least one trail should start with IsMultiRegionTrail=True
            valid_trails = [t for t in trails if t.get('IsMultiRegionTrail')]
            
            status = FindingStatus.PASS if valid_trails else FindingStatus.FAIL
            
            return self.build_finding(
                check_id="check_cloudtrail_enabled",
                status=status,
                resource_id="multi-region-trail",
                resource_type="AWS::CloudTrail::Trail",
                evidence={
                    "total_trails": len(trails),
                    "multi_region_trails": len(valid_trails),
                    "trail_names": [t.get('Name') for t in valid_trails]
                }
            )
        except Exception as e:
            logger.warning(f"Failed check 2.1: {e}")
            return None

    def _check_log_file_validation(self, client) -> List[Dict[str, Any]]:
        """
        CIS 2.2: Ensure CloudTrail log file validation is enabled.
        """
        findings = []
        try:
            response = client.describe_trails()
            trails = response.get('trailList', [])
            
            if not trails:
                # If no trails exist, this check fails as you can't have validation enabled on nothing.
                # However, CIS 2.1 would already flag "no trails".
                # We can return valid "FAIL" finding.
                return [self.build_finding(
                    check_id="check_cloudtrail_validation",
                    status=FindingStatus.FAIL,
                    resource_id="no-trails-found",
                    resource_type="AWS::CloudTrail::Trail",
                    evidence={"error": "No CloudTrail trails found"}
                )]

            for trail in trails:
                arn = trail.get('TrailARN')
                name = trail.get('Name')
                validation_enabled = trail.get('LogFileValidationEnabled', False)
                
                status = FindingStatus.PASS if validation_enabled else FindingStatus.FAIL
                
                evidence = {
                   "LogFileValidationEnabled": validation_enabled,
                   "TrailName": name,
                   "HomeRegion": trail.get('HomeRegion')
                }

                findings.append(self.build_finding(
                    check_id="check_cloudtrail_validation",
                    status=status,
                    resource_id=name,
                    resource_type="AWS::CloudTrail::Trail",
                    evidence=evidence
                ))
                 
        except Exception as e:
            logger.warning(f"Failed check 2.2: {e}")
            
        return findings
