from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List, Any
import boto3
from datetime import datetime, timedelta

from models import get_db
from models.resource import Resource
from models.service import AWSService
from services.aws.scanner_base import ScannerBase
from core.aws_client import get_aws_client_factory
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class RightSizingScanner(ScannerBase):
    """Temporary scanner subclass to utilize base methods"""
    def __init__(self, region: str = 'us-east-1'):
        super().__init__(region)
        
    def service_name(self) -> str: return "RightSizing"
    def service_code(self) -> str: return "RightSizing"
    def service_category(self) -> str: return "Optimization"
    def scan(self) -> List[Dict[str, Any]]: return []
    def identify_unused(self, resource: Dict) -> bool: return False
    
    def get_instance_metrics(self, instance_id: str, days: int = 7) -> List[Dict]:
        """Get CPU metrics for an instance"""
        return self.get_cloudwatch_metrics(
            namespace='AWS/EC2',
            metric_name='CPUUtilization',
            dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            days=days
        )

@router.get("/rightsizing/recommendations")
async def get_rightsizing_recommendations(
    region: str = 'us-east-1',
    days: int = 7,
    cpu_threshold: float = 10.0,
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Analyze EC2 instances for right-sizing opportunities.
    
    Identifies instances with low CPU utilization (< 10% avg) 
    that could be downgraded to a smaller instance type.
    """
    try:
        # 1. Get active EC2 instances from DB
        # We need the resource_id (instance ID) and current type
        query = (
            select(Resource)
            .join(AWSService)
            .where(
                Resource.resource_type == 'AWS::EC2::Instance',
                Resource.region == region,
                # Simple check for active services (could also check last_seen)
            )
        )
        result = await db.execute(query)
        instances = result.scalars().all()
        
        recommendations = []
        scanner = RightSizingScanner(region=region)
        
        for instance in instances:
            # 2. Get CloudWatch metrics (FREE basic metrics)
            metrics = scanner.get_instance_metrics(instance.resource_id, days=days)
            
            if not metrics:
                continue
                
            # Calculate average CPU
            avg_cpu = sum(p['Average'] for p in metrics) / len(metrics)
            max_cpu = max(p['Maximum'] for p in metrics)
            
            # 3. Analyze for right-sizing
            if avg_cpu < cpu_threshold and max_cpu < (cpu_threshold * 2):
                # Simple Logic: Suggest 1 size down in same family
                # e.g., t3.large -> t3.medium
                current_type = instance.resource_config.get('InstanceType', 'unknown')
                suggested_type = _suggest_downgrade(current_type)
                
                if suggested_type:
                    estimated_savings = float(instance.cost_monthly) * 0.5  # Rough estimate: 50% savings
                    
                    recommendations.append({
                        'instance_id': instance.resource_id,
                        'name': instance.resource_name,
                        'current_type': current_type,
                        'suggested_type': suggested_type,
                        'avg_cpu': round(avg_cpu, 2),
                        'max_cpu': round(max_cpu, 2),
                        'estimated_monthly_savings': round(estimated_savings, 2),
                        'confidence': 'High' if days >= 7 else 'Low'
                    })
        
        return {
            'total_analyzed': len(instances),
            'opportunities_found': len(recommendations),
            'total_potential_savings': sum(r['estimated_monthly_savings'] for r in recommendations),
            'recommendations': recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating right-sizing recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _suggest_downgrade(instance_type: str) -> str:
    """
    Suggests a smaller instance type within the same family.
    Very basic logic for demonstration.
    """
    if not instance_type or '.' not in instance_type:
        return None
        
    family, size = instance_type.split('.')
    
    # Simple size map (descending order)
    sizes = ['24xlarge', '16xlarge', '12xlarge', '8xlarge', '4xlarge', '2xlarge', 'xlarge', 'large', 'medium', 'small', 'micro', 'nano']
    
    try:
        current_idx = sizes.index(size)
        if current_idx < len(sizes) - 1:
            return f"{family}.{sizes[current_idx + 1]}"
    except ValueError:
        pass
        
    return None
