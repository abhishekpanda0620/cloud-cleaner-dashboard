from typing import List, Dict, Any
from ..scanner_base import ScannerBase
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EC2OtherScanner(ScannerBase):
    """
    Scanner for 'EC2-Other' category resources.
    Aggregates:
    1. EBS Snapshots
    2. Elastic IPs (Unattached)
    """
    
    def service_name(self) -> str:
        return "EC2 - Other"
        
    def service_code(self) -> str:
        return "EC2Other"
        
    def service_category(self) -> str:
        return "Infrastructure"

    def scan(self) -> List[Dict[str, Any]]:
        resources = []
        resources.extend(self._scan_snapshots())
        resources.extend(self._scan_eips())
        return resources

    def _scan_snapshots(self) -> List[Dict[str, Any]]:
        try:
            client = self.get_client('ec2')
            # Get snapshots owned by self
            response = client.describe_snapshots(OwnerIds=['self'])
            
            resources = []
            for snap in response.get('Snapshots', []):
                resources.append({
                    'resource_id': snap['SnapshotId'],
                    'resource_type': 'AWS::EC2::Snapshot',
                    'resource_name': f"Snapshot ({snap['VolumeSize']} GB)",
                    'region': self.region,
                    'is_unused': False, # Default
                    'resource_config': {
                        'VolumeSize': snap['VolumeSize'],
                        'StartTime': snap['StartTime'].isoformat(),
                        'State': snap['State'],
                        'Description': snap.get('Description', '')
                    },
                    'tags': {t['Key']: t['Value'] for t in snap.get('Tags', [])}
                })
            return resources
        except Exception as e:
            logger.error(f"Error scanning snapshots: {e}")
            return []

    def _scan_eips(self) -> List[Dict[str, Any]]:
        try:
            client = self.get_client('ec2')
            response = client.describe_addresses()
            
            resources = []
            for addr in response.get('Addresses', []):
                is_unused = 'InstanceId' not in addr
                resources.append({
                    'resource_id': addr['AllocationId'],
                    'resource_type': 'AWS::EC2::EIP',
                    'resource_name': addr['PublicIp'],
                    'region': self.region,
                    'is_unused': is_unused,
                    'unused_reason': 'Not attached to any instance' if is_unused else None,
                    'resource_config': {
                        'PublicIp': addr['PublicIp'],
                        'Domain': addr.get('Domain'),
                        'AssociationId': addr.get('AssociationId'),
                    },
                    'tags': {t['Key']: t['Value'] for t in addr.get('Tags', [])}
                })
            return resources
        except Exception as e:
            logger.error(f"Error scanning EIPs: {e}")
            return []

    def identify_unused(self, resource: Dict) -> bool:
        resource_type = resource.get('resource_type')
        
        if resource_type == 'AWS::EC2::EIP':
            return resource.get('is_unused', False)
            
        if resource_type == 'AWS::EC2::Snapshot':
            # Logic: If older than 30 days
            try:
                config = resource.get('resource_config', {})
                start_time = datetime.fromisoformat(config['StartTime'])
                age_days = (datetime.now(start_time.tzinfo) - start_time).days
                if age_days > 30:
                    resource['unused_reason'] = f"Snapshot is {age_days} days old"
                    return True
            except:
                pass
                
        return False
