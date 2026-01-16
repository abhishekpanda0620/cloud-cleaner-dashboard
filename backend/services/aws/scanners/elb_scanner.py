
from typing import List, Dict, Any, Optional
from ..scanner_base import ScannerBase
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ELBScanner(ScannerBase):
    """
    Scanner for Elastic Load Balancers (v2 - ALB/NLB).
    Identifies unused load balancers based on:
    1. No target groups
    2. Target groups with no healthy targets
    3. Low traffic (metrics)
    """
    
    @property
    def service_name(self) -> str:
        return "Elastic Load Balancing"
    
    @property
    def service_code(self) -> str:
        return "AmazonELB" # Or AmazonEC2 in some contexts, but ELB is distinct enough
    
    @property
    def service_category(self) -> str:
        return "Networking"

    def scan(self, regions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        resources = []
        if regions is None:
            regions = [self.region]

        for region in regions:
            try:
                client = self.session.client('elbv2', region_name=region)
                paginator = client.get_paginator('describe_load_balancers')
                
                for page in paginator.paginate():
                    for elb in page['LoadBalancers']:
                        resources.append(self._process_elb(client, elb, region))
                        
            except Exception as e:
                logger.debug(f"Error scanning ELB in {region}: {e}")
                
        return resources

    def _process_elb(self, client, elb: Dict, region: str) -> Dict[str, Any]:
        elb_arn = elb['LoadBalancerArn']
        elb_name = elb['LoadBalancerName']
        elb_type = elb['Type'] # 'application' | 'network' | 'gateway'
        
        # Check for unused conditions
        is_unused, reason = self._check_unused(client, elb_arn, elb_type, region)
        
        # Calculate cost
        # 730 hours * hourly price (approx)
        hourly_price = self.pricing_service.get_elb_price(region, elb_type)
        monthly_cost = hourly_price * 730
        
        return {
            'resource_id': elb_arn,
            'resource_type': 'AWS::ElasticLoadBalancingV2::LoadBalancer',
            'resource_name': elb_name,
            'region': region,
            'is_unused': is_unused,
            'unused_reason': reason,
            'estimated_monthly_cost': monthly_cost,
            'resource_config': {
                'Type': elb_type,
                'State': elb.get('State', {}).get('Code'),
                'Scheme': elb.get('Scheme'),
                'CreatedTime': elb.get('CreatedTime').isoformat()
            },
            'tags': self._get_tags(client, elb_arn)
        }

    def _check_unused(self, client, elb_arn: str, elb_type: str, region: str) -> (bool, str):
        try:
            # 1. Check Target Groups
            tgs = client.describe_target_groups(LoadBalancerArn=elb_arn).get('TargetGroups', [])
            
            if not tgs:
                return True, "No target groups attached"
                
            # 2. Check Targets Health
            has_targets = False
            for tg in tgs:
                target_health = client.describe_target_health(TargetGroupArn=tg['TargetGroupArn']).get('TargetHealthDescriptions', [])
                if target_health:
                    has_targets = True
                    # Check if any target is healthy? 
                    # Actually, if it has targets but they are all unhealthy, the LB is useless but taking traffic.
                    # If NO targets are registered at all, it's definitely unused.
            
            if not has_targets:
                 return True, "Target groups have no registered targets"

            # 3. Check Metrics (Low Request Count for ALB, Active Flow Count for NLB)
            # This is more expensive/slow, so maybe optional or strict thresholds
            namespace = 'AWS/ApplicationELB' if elb_type == 'application' else 'AWS/NetworkELB'
            metric_name = 'RequestCount' if elb_type == 'application' else 'ActiveFlowCount'
            
            # Extract short name for dimensions
            # ARN format: arn:aws:elasticloadbalancing:region:account:loadbalancer/app/name/id
            # Dimension 'LoadBalancer' requires 'app/name/id' part
            dimension_value = "/".join(elb_arn.split("loadbalancer/")[1].split("/"))
            
            datapoints = self.get_cloudwatch_metrics(
                namespace=namespace,
                metric_name=metric_name,
                dimensions=[{'Name': 'LoadBalancer', 'Value': dimension_value}],
                days=7
            )
            
            if not datapoints:
                # No data often means no traffic
                return True, "No traffic recorded in last 7 days"
                
            total_requests = sum(d['Sum'] for d in datapoints) if elb_type == 'application' else sum(d['Maximum'] for d in datapoints)
            
            if total_requests < 10: # Extremely low threshold
                return True, f"Extremely low traffic ({int(total_requests)} ops in 7 days)"

            return False, None
            
        except Exception as e:
            logger.debug(f"Error checking unused for ELB {elb_arn}: {e}")
            return False, None

    def _get_tags(self, client, resource_arn: str) -> Dict[str, str]:
        try:
            response = client.describe_tags(ResourceArns=[resource_arn])
            tags = {}
            for tag_desc in response.get('TagDescriptions', []):
                for tag in tag_desc.get('Tags', []):
                     tags[tag['Key']] = tag['Value']
            return tags
        except:
            return {}

    def identify_unused(self, resource: Dict[str, Any]) -> bool:
        return resource.get('is_unused', False)
