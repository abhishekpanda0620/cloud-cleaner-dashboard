from typing import List, Dict, Any
import logging
from .base import SecurityScannerBase
from models.security import FindingStatus

logger = logging.getLogger(__name__)

class MonitoringSecurityScanner(SecurityScannerBase):
    
    @property
    def service_name(self) -> str:
        return "CloudWatch"

    def run_checks(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            logs_client = self.session.client('logs', region_name=self.region)
            cw_client = self.session.client('cloudwatch', region_name=self.region)
            
            # Helper to get all metric filters
            # Realistically we should look for specific patterns.
            # CIS 4.1 Ensure a log metric filter and alarm exist for unauthorized API calls
            # CIS 4.2 ... for Management Console sign-in without MFA
            # CIS 4.3 ... for usage of "root" account
            
            # For MVP, we will check for "Root Account Usage" filter.
            # Pattern: { $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent" }
            
            findings.append(self._check_root_usage_alarm(logs_client, cw_client))

        except Exception as e:
            logger.error(f"Error running Monitoring security checks: {e}")
            
        return [f for f in findings if f]

    def _check_root_usage_alarm(self, logs_client, cw_client) -> Dict[str, Any]:
        """
        CIS 4.3: Ensure a log metric filter and alarm exist for usage of "root" account.
        """
        try:
            # 1. Get Metric Filters
            # This is hard because we have to scan ALL log groups or know which one is CloudTrail.
            # Usually CloudTrail logs to a specific group.
            # We will iterate describe_metric_filters() (paginated) and look for the pattern.
            
            paginator = logs_client.get_paginator('describe_metric_filters')
            found_filter = None
            
            # Simplified pattern check (contains "Root")
            for page in paginator.paginate():
                for mf in page['metricFilters']:
                    pattern = mf.get('filterPattern', '')
                    if 'Root' in pattern and 'userIdentity.type' in pattern:
                        found_filter = mf
                        break
                if found_filter: break
            
            if not found_filter:
                 return self.build_finding(
                    check_id="check_root_usage_alarm",
                    status=FindingStatus.FAIL,
                    resource_id="cis-4.3-root-usage",
                    resource_type="AWS::CloudWatch::Alarm",
                    evidence={"error": "No metric filter found for Root usage"}
                )
            
            # 2. Check if Alarm exists for this metric
            metric_name = found_filter.get('metricTransformations', [{}])[0].get('metricName')
            metric_ns = found_filter.get('metricTransformations', [{}])[0].get('metricNamespace')
            
            if not metric_name:
                 return self.build_finding(
                    check_id="check_root_usage_alarm",
                    status=FindingStatus.FAIL,
                    resource_id="cis-4.3-root-usage",
                    resource_type="AWS::CloudWatch::Alarm",
                    evidence={"error": "Metric filter exists but no metric definition"}
                )
            
            # Check alarms
            alarms = cw_client.describe_alarms_for_metric(
                MetricName=metric_name,
                Namespace=metric_ns
            )
            
            has_alarm = len(alarms.get('MetricAlarms', [])) > 0
            
            status = FindingStatus.PASS if has_alarm else FindingStatus.FAIL
            
            return self.build_finding(
                check_id="check_root_usage_alarm",
                status=status,
                resource_id="cis-4.3-root-usage",
                resource_type="AWS::CloudWatch::Alarm",
                evidence={
                    "metric_filter": found_filter['filterName'],
                    "alarm_count": len(alarms.get('MetricAlarms', []))
                }
            )

        except Exception as e:
            logger.warning(f"Failed check monitoring: {e}")
            return None
