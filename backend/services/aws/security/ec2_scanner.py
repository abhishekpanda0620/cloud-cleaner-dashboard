from typing import List, Dict, Any
import logging
from .base import SecurityScannerBase
from models.security import FindingStatus

logger = logging.getLogger(__name__)

class EC2SecurityScanner(SecurityScannerBase):
    
    @property
    def service_name(self) -> str:
        return "EC2"

    def run_checks(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            ec2_client = self.session.client('ec2', region_name=self.region)
            
            # CIS 4.1 Ensure no security groups allow ingress from 0.0.0.0/0 to remote server administration ports
            findings.extend(self._check_security_group_ingress(ec2_client))

            # CIS 4.4 Ensure the default security group of every VPC restricts all traffic
            findings.extend(self._check_default_security_group_closed(ec2_client))
            
            # CIS 3.5 Ensure VPC Flow Logs are enabled for all VPCs
            findings.extend(self._check_vpc_flow_logs(ec2_client))
            
        except Exception as e:
            logger.error(f"Error running EC2 security checks: {e}")
            
        return findings

    def _check_security_group_ingress(self, client) -> List[Dict[str, Any]]:
        """
        CIS 4.1: Ensure no security groups allow ingress from 0.0.0.0/0 to ports 22 or 3389.
        """
        findings = []
        try:
            # We want to find groups that violate this.
            # Filter for active SGs
            paginator = client.get_paginator('describe_security_groups')
            
            for page in paginator.paginate():
                for sg in page['SecurityGroups']:
                    sg_id = sg['GroupId']
                    sg_name = sg['GroupName']
                    
                    # Check ingress rules
                    violations = []
                    
                    for permission in sg.get('IpPermissions', []):
                        from_port = permission.get('FromPort')
                        to_port = permission.get('ToPort')
                        ip_protocol = permission.get('IpProtocol')
                        
                        # Check if rule covers 22 or 3389
                        # Protocol -1 means all.
                        # TCP/UDP checks.
                        
                        is_risk_port = False
                        if ip_protocol == '-1':
                            is_risk_port = True
                        elif ip_protocol == 'tcp':
                            if from_port is None or to_port is None:
                                continue # Invalid rule?
                            
                            # Check overlap with 22 or 3389
                            # Range includes target?
                            if (from_port <= 22 <= to_port) or (from_port <= 3389 <= to_port):
                                is_risk_port = True
                        
                        if is_risk_port:
                            # Check if source is 0.0.0.0/0
                            for ip_range in permission.get('IpRanges', []):
                                if ip_range.get('CidrIp') == '0.0.0.0/0':
                                    violations.append(f"Port {from_port}-{to_port} open to 0.0.0.0/0")
                                    
                            for ip_range in permission.get('Ipv6Ranges', []):
                                if ip_range.get('CidrIpv6') == '::/0':
                                    violations.append(f"Port {from_port}-{to_port} open to ::/0")

                    if violations:
                        findings.append(self.build_finding(
                            check_id="check_sg_open_ports", 
                            status=FindingStatus.FAIL,
                            resource_id=sg_id,
                            resource_type="AWS::EC2::SecurityGroup",
                            evidence={"violations": violations, "group_name": sg_name}
                        ))
                    
                    else:
                        findings.append(self.build_finding(
                            check_id="check_sg_open_ports",
                            status=FindingStatus.PASS,
                            resource_id=sg_id,
                            resource_type="AWS::EC2::SecurityGroup",
                            evidence={"group_name": sg_name}
                        ))
                        
        except Exception as e:
            logger.warning(f"Failed check 4.1: {e}")
            
        return findings

    def _check_default_security_group_closed(self, client) -> List[Dict[str, Any]]:
        """
        CIS 4.4: Ensure the default security group of every VPC restricts all traffic.
        """
        findings = []
        try:
            # Filter for default security groups
            response = client.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': ['default']}])
            
            for sg in response.get('SecurityGroups', []):
                sg_id = sg['GroupId']
                vpc_id = sg.get('VpcId', 'unknown')
                
                # Check Ingress and Egress
                ingress = sg.get('IpPermissions', [])
                egress = sg.get('IpPermissionsEgress', [])
                
                # CIS recommends both should be empty (no rules)
                
                is_compliant = (len(ingress) == 0 and len(egress) == 0)
                
                status = FindingStatus.PASS if is_compliant else FindingStatus.FAIL
                
                evidence = {
                    "vpc_id": vpc_id,
                    "ingress_rules_count": len(ingress),
                    "egress_rules_count": len(egress)
                }
                
                findings.append(self.build_finding(
                    check_id="check_default_sg_restricted",
                    status=status,
                    resource_id=sg_id,
                    resource_type="AWS::EC2::SecurityGroup",
                    evidence=evidence
                ))

        except Exception as e:
            logger.warning(f"Failed check 4.4: {e}")
            
        return findings

    def _check_vpc_flow_logs(self, client) -> List[Dict[str, Any]]:
        """
        CIS 3.5: Ensure VPC Flow Logs are enabled for all VPCs.
        """
        findings = []
        try:
            # Get all VPCs
            vpcs = client.describe_vpcs().get('Vpcs', [])
            
            for vpc in vpcs:
                vpc_id = vpc['VpcId']
                
                # Check for Flow Logs attached to this VPC
                # Filter by resource-id = vpc_id
                flow_logs = client.describe_flow_logs(
                    Filters=[{'Name': 'resource-id', 'Values': [vpc_id]}]
                ).get('FlowLogs', [])
                
                # Must be active
                active_logs = [fl for fl in flow_logs if fl.get('FlowLogStatus') == 'ACTIVE']
                
                status = FindingStatus.PASS if active_logs else FindingStatus.FAIL
                
                findings.append(self.build_finding(
                    check_id="check_vpc_flow_logs",
                    status=status,
                    resource_id=vpc_id,
                    resource_type="AWS::EC2::VPC",
                    evidence={
                        "flow_logs_count": len(flow_logs),
                        "active_logs_count": len(active_logs)
                    }
                ))
                
        except Exception as e:
             logger.warning(f"Failed check 3.5: {e}")
             
        return findings
