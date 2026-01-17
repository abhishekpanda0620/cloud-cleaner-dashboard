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
            
            # CIS 4.1 - 4.15 Pattern Definitions
            monitoring_checks = [
                {
                    "id": "check_unauthorized_api", 
                    "cis_id": "4.1",
                    "name": "Ensure a log metric filter and alarm exist for unauthorized API calls",
                    "pattern": '{($.errorCode = "*UnauthorizedOperation") || ($.errorCode = "AccessDenied*")}'
                },
                {
                    "id": "check_no_mfa_console",
                    "cis_id": "4.2", 
                    "name": "Ensure a log metric filter and alarm exist for Management Console sign-in without MFA",
                    "pattern": '{($.eventName = "ConsoleLogin") && ($.additionalEventData.MFAUsed != "Yes")}'
                },
                {
                    "id": "check_root_usage",
                    "cis_id": "4.3",
                    "name": "Ensure a log metric filter and alarm exist for usage of 'root' account",
                    "pattern": '{$.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent"}'
                },
                {
                    "id": "check_iam_policy_changes",
                    "cis_id": "4.4",
                    "name": "Ensure a log metric filter and alarm exist for IAM policy changes",
                    "pattern": '{($.eventName=DeleteGroupPolicy)||($.eventName=DeleteRolePolicy)||($.eventName=DeleteUserPolicy)||($.eventName=PutGroupPolicy)||($.eventName=PutRolePolicy)||($.eventName=PutUserPolicy)||($.eventName=CreatePolicy)||($.eventName=DeletePolicy)||($.eventName=CreatePolicyVersion)||($.eventName=DeletePolicyVersion)||($.eventName=AttachRolePolicy)||($.eventName=DetachRolePolicy)||($.eventName=AttachUserPolicy)||($.eventName=DetachUserPolicy)||($.eventName=AttachGroupPolicy)||($.eventName=DetachGroupPolicy)}'
                },
                {
                    "id": "check_cloudtrail_cfg_changes",
                    "cis_id": "4.5",
                    "name": "Ensure a log metric filter and alarm exist for CloudTrail configuration changes",
                    "pattern": '{($.eventName = CreateTrail) || ($.eventName = UpdateTrail) || ($.eventName = DeleteTrail) || ($.eventName = StartLogging) || ($.eventName = StopLogging)}'
                },
                {
                    "id": "check_console_auth_failure",
                    "cis_id": "4.6",
                    "name": "Ensure a log metric filter and alarm exist for AWS Management Console authentication failures",
                    "pattern": '{($.eventName = ConsoleLogin) && ($.errorMessage = "Failed authentication")}'
                },
                {
                    "id": "check_disable_delete_kms",
                    "cis_id": "4.7",
                    "name": "Ensure a log metric filter and alarm exist for disabling or scheduled deletion of customer created CMKs",
                    "pattern": '{($.eventSource = kms.amazonaws.com) && (($.eventName = DisableKey) || ($.eventName = ScheduleKeyDeletion))}'
                },
                {
                    "id": "check_s3_bucket_policy",
                    "cis_id": "4.8",
                    "name": "Ensure a log metric filter and alarm exist for S3 bucket policy changes",
                    "pattern": '{($.eventSource = s3.amazonaws.com) && (($.eventName = PutBucketAcl) || ($.eventName = PutBucketPolicy) || ($.eventName = PutBucketCors) || ($.eventName = PutBucketLifecycle) || ($.eventName = PutBucketReplication) || ($.eventName = DeleteBucketPolicy) || ($.eventName = DeleteBucketCors) || ($.eventName = DeleteBucketLifecycle) || ($.eventName = DeleteBucketReplication))}'
                },
                {
                    "id": "check_config_change",
                    "cis_id": "4.9",
                    "name": "Ensure a log metric filter and alarm exist for AWS Config configuration changes",
                    "pattern": '{($.eventSource = config.amazonaws.com) && (($.eventName=StopConfigurationRecorder)||($.eventName=DeleteDeliveryChannel)||($.eventName=PutDeliveryChannel)||($.eventName=PutConfigurationRecorder))}'
                },
                {
                    "id": "check_security_group_changes",
                    "cis_id": "4.10",
                    "name": "Ensure a log metric filter and alarm exist for security group changes",
                    "pattern": '{($.eventName = AuthorizeSecurityGroupIngress) || ($.eventName = AuthorizeSecurityGroupEgress) || ($.eventName = RevokeSecurityGroupIngress) || ($.eventName = RevokeSecurityGroupEgress) || ($.eventName = CreateSecurityGroup) || ($.eventName = DeleteSecurityGroup)}'
                },
                {
                    "id": "check_nacl_changes",
                    "cis_id": "4.11",
                    "name": "Ensure a log metric filter and alarm exist for changes to Network Access Control Lists (NACL)",
                    "pattern": '{($.eventName = CreateNetworkAcl) || ($.eventName = CreateNetworkAclEntry) || ($.eventName = DeleteNetworkAcl) || ($.eventName = DeleteNetworkAclEntry) || ($.eventName = ReplaceNetworkAclEntry) || ($.eventName = ReplaceNetworkAclAssociation)}'
                },
                {
                    "id": "check_network_gateway_changes",
                    "cis_id": "4.12",
                    "name": "Ensure a log metric filter and alarm exist for changes to network gateways",
                    "pattern": '{($.eventName = CreateCustomerGateway) || ($.eventName = DeleteCustomerGateway) || ($.eventName = AttachInternetGateway) || ($.eventName = CreateInternetGateway) || ($.eventName = DeleteInternetGateway) || ($.eventName = DetachInternetGateway)}'
                },
                {
                    "id": "check_route_table_changes",
                    "cis_id": "4.13",
                    "name": "Ensure a log metric filter and alarm exist for route table changes",
                    "pattern": '{($.eventName = CreateRoute) || ($.eventName = CreateRouteTable) || ($.eventName = ReplaceRoute) || ($.eventName = ReplaceRouteTableAssociation) || ($.eventName = DeleteRouteTable) || ($.eventName = DeleteRoute) || ($.eventName = DisassociateRouteTable)}'
                },
                {
                    "id": "check_vpc_changes",
                    "cis_id": "4.14",
                    "name": "Ensure a log metric filter and alarm exist for VPC changes",
                    "pattern": '{($.eventName = CreateVpc) || ($.eventName = DeleteVpc) || ($.eventName = ModifyVpcAttribute) || ($.eventName = AcceptVpcPeeringConnection) || ($.eventName = CreateVpcPeeringConnection) || ($.eventName = DeleteVpcPeeringConnection) || ($.eventName = RejectVpcPeeringConnection) || ($.eventName = AttachClassicLinkVpc) || ($.eventName = DetachClassicLinkVpc) || ($.eventName = DisableVpcClassicLink) || ($.eventName = EnableVpcClassicLink)}'
                },
                # Note: 4.15 is "Ensure a log metric filter and alarm exist for AWS Organizations changes" 
                # but might be noisy/optional. Including for completeness.
                {
                    "id": "check_org_changes",
                    "cis_id": "4.15",
                    "name": "Ensure a log metric filter and alarm exist for AWS Organizations changes",
                    "pattern": '{($.eventSource = organizations.amazonaws.com) && (($.eventName = "AcceptHandshake") || ($.eventName = "AttachPolicy") || ($.eventName = "CreateAccount") || ($.eventName = "CreateOrganizationalUnit") || ($.eventName = "CreatePolicy") || ($.eventName = "DeclineHandshake") || ($.eventName = "DeleteOrganizationalUnit") || ($.eventName = "DeletePolicy") || ($.eventName = "DetachPolicy") || ($.eventName = "DisablePolicyType") || ($.eventName = "EnablePolicyType") || ($.eventName = "InviteAccountToOrganization") || ($.eventName = "LeaveOrganization") || ($.eventName = "MoveAccount") || ($.eventName = "RemoveAccountFromOrganization") || ($.eventName = "UpdatePolicy") || ($.eventName = "UpdateOrganizationalUnit"))}'
                }
            ]
            
            # Fetch all metric filters once to avoid API throttling
            # This is an optimization: Get all filters, then match against patterns.
            # In a huge account this might need pagination loop.
            all_filters = self._get_all_metric_filters(logs_client)
            
            for check in monitoring_checks:
                findings.append(self._check_filter_and_alarm(all_filters, cw_client, check))

        except Exception as e:
            logger.error(f"Error running Monitoring security checks: {e}")
            
        return [f for f in findings if f]

    def _get_all_metric_filters(self, logs_client) -> List[Dict[str, Any]]:
        filters = []
        try:
            paginator = logs_client.get_paginator('describe_metric_filters')
            for page in paginator.paginate():
                filters.extend(page.get('metricFilters', []))
        except Exception as e:
            logger.error(f"Failed to fetch metric filters: {e}")
        return filters

    def _check_filter_and_alarm(self, all_filters: List[Dict], cw_client, check_def: Dict) -> Dict[str, Any]:
        """
        Generic check logic: 
        1. Find Metric Filter matching the pattern.
        2. Ensure Metric Filter points to a Metric.
        3. Ensure an Alarm exists for that Metric.
        """
        target_pattern = check_def['pattern']
        
        # 1. Find Filter
        # Note: Exact string match on pattern might be brittle if user has extra spaces.
        # Ideally we parse/normalize, but for MVP we strip spaces or do partial match.
        # We will try exact match first, then loose match.
        found_filter = None
        
        # Normalize target pattern (basic strip)
        target_norm = target_pattern.replace(" ", "")
        
        for mf in all_filters:
            pat = mf.get('filterPattern', '')
            if not pat: continue
            
            if pat.replace(" ", "") == target_norm:
                found_filter = mf
                break
        
        if not found_filter:
             return self.build_finding(
                check_id=check_def['id'],
                status=FindingStatus.FAIL,
                resource_id=f"cis-{check_def['cis_id']}",
                resource_type="AWS::CloudWatch::Alarm",
                evidence={"error": f"No metric filter found matching pattern: {target_pattern}"}
            )
        
        # 2. Check for Metric Transformation
        transformations = found_filter.get('metricTransformations', [])
        if not transformations:
             return self.build_finding(
                check_id=check_def['id'],
                status=FindingStatus.FAIL,
                resource_id=f"cis-{check_def['cis_id']}",
                resource_type="AWS::CloudWatch::Alarm",
                evidence={"error": "Metric filter found but has no metric transformations"}
            )
            
        metric_name = transformations[0].get('metricName')
        metric_ns = transformations[0].get('metricNamespace')
        
        # 3. Check for Alarms
        try:
            alarms_resp = cw_client.describe_alarms_for_metric(
                MetricName=metric_name,
                Namespace=metric_ns
            )
            alarms = alarms_resp.get('MetricAlarms', [])
            
            has_alarm = len(alarms) > 0
            status = FindingStatus.PASS if has_alarm else FindingStatus.FAIL
            
            return self.build_finding(
                check_id=check_def['id'],
                status=status,
                resource_id=f"cis-{check_def['cis_id']}",
                resource_type="AWS::CloudWatch::Alarm",
                evidence={
                    "metric_filter": found_filter.get('filterName'),
                    "alarm_name": alarms[0]['AlarmName'] if has_alarm else None,
                    "alarm_count": len(alarms)
                }
            )
        except Exception as e:
             return self.build_finding(
                check_id=check_def['id'],
                status=FindingStatus.FAIL,
                resource_id=f"cis-{check_def['cis_id']}",
                resource_type="AWS::CloudWatch::Alarm",
                evidence={"error": f"Failed to check alarms: {str(e)}"}
            )
