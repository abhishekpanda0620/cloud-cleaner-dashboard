from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, List
import io
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from core.aws_client import get_aws_client_factory
from core.cache import get_cache

router = APIRouter()

def get_pricing_client():
    """Get AWS Pricing API client (us-east-1 only)"""
    return boto3.client('pricing', region_name='us-east-1')

def get_cost_explorer_client():
    """Get AWS Cost Explorer client"""
    return boto3.client('ce', region_name='us-east-1')

def get_ec2_pricing(instance_type: str, region: str = 'us-east-1') -> float:
    """Get EC2 instance pricing from AWS Pricing API"""
    try:
        pricing_client = get_pricing_client()
        
        response = pricing_client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': get_region_name(region)},
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'}
            ],
            MaxResults=1
        )
        
        if response['PriceList']:
            import json
            price_data = json.loads(response['PriceList'][0])
            on_demand = price_data['terms']['OnDemand']
            price_dimensions = list(on_demand.values())[0]['priceDimensions']
            price_per_hour = float(list(price_dimensions.values())[0]['pricePerUnit']['USD'])
            # Convert to monthly (730 hours average)
            return price_per_hour * 730
        
        return 20.0  # Default fallback
        
    except Exception as e:
        print(f"Error fetching EC2 pricing: {e}")
        return 20.0  # Default fallback

def get_ebs_pricing(region: str = 'us-east-1') -> float:
    """Get EBS pricing per GB from AWS Pricing API"""
    try:
        pricing_client = get_pricing_client()
        
        response = pricing_client.get_products(
            ServiceCode='AmazonEC2',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage'},
                {'Type': 'TERM_MATCH', 'Field': 'volumeApiName', 'Value': 'gp2'},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': get_region_name(region)}
            ],
            MaxResults=1
        )
        
        if response['PriceList']:
            import json
            price_data = json.loads(response['PriceList'][0])
            on_demand = price_data['terms']['OnDemand']
            price_dimensions = list(on_demand.values())[0]['priceDimensions']
            price_per_gb = float(list(price_dimensions.values())[0]['pricePerUnit']['USD'])
            return price_per_gb
        
        return 0.10  # Default fallback
        
    except Exception as e:
        print(f"Error fetching EBS pricing: {e}")
        return 0.10  # Default fallback

def get_s3_pricing() -> float:
    """Get S3 pricing per GB from AWS Pricing API"""
    try:
        pricing_client = get_pricing_client()
        
        response = pricing_client.get_products(
            ServiceCode='AmazonS3',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Storage'},
                {'Type': 'TERM_MATCH', 'Field': 'storageClass', 'Value': 'General Purpose'},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'}
            ],
            MaxResults=1
        )
        
        if response['PriceList']:
            import json
            price_data = json.loads(response['PriceList'][0])
            on_demand = price_data['terms']['OnDemand']
            price_dimensions = list(on_demand.values())[0]['priceDimensions']
            price_per_gb = float(list(price_dimensions.values())[0]['pricePerUnit']['USD'])
            return price_per_gb
        
        return 0.023  # Default fallback
        
    except Exception as e:
        print(f"Error fetching S3 pricing: {e}")
        return 0.023  # Default fallback

def get_region_name(region_code: str) -> str:
    """Convert region code to region name for Pricing API"""
    region_names = {
        'us-east-1': 'US East (N. Virginia)',
        'us-east-2': 'US East (Ohio)',
        'us-west-1': 'US West (N. California)',
        'us-west-2': 'US West (Oregon)',
        'eu-west-1': 'EU (Ireland)',
        'eu-central-1': 'EU (Frankfurt)',
        'ap-southeast-1': 'Asia Pacific (Singapore)',
        'ap-northeast-1': 'Asia Pacific (Tokyo)',
    }
    return region_names.get(region_code, 'US East (N. Virginia)')

def get_actual_costs_from_cost_explorer(days: int = 30) -> Dict:
    """Get actual costs from AWS Cost Explorer"""
    try:
        ce_client = get_cost_explorer_client()
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )
        
        # Process cost data
        daily_costs = {}
        for result in response['ResultsByTime']:
            date = result['TimePeriod']['Start']
            total_cost = 0.0
            
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                total_cost += cost
            
            daily_costs[date] = total_cost
        
        return daily_costs
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("Cost Explorer access denied. Using estimated costs.")
            return {}
        raise

def estimate_ec2_cost(instance: Dict, region: str = 'us-east-1') -> float:
    """Estimate monthly cost for an EC2 instance using AWS Pricing API"""
    instance_type = instance.get('instance_type', 't2.micro')
    return get_ec2_pricing(instance_type, region)

def estimate_ebs_cost(volume: Dict, region: str = 'us-east-1') -> float:
    """Estimate monthly cost for an EBS volume using AWS Pricing API"""
    size = volume.get('size', 0)
    price_per_gb = get_ebs_pricing(region)
    return size * price_per_gb

def estimate_s3_cost(bucket: Dict) -> float:
    """Estimate monthly cost for an S3 bucket using AWS Pricing API"""
    # Simplified: assume 10GB average for unused buckets
    size = bucket.get('size_gb', 10)
    price_per_gb = get_s3_pricing()
    return size * price_per_gb

def calculate_resource_costs(resource_type: str, resources: List[Dict], region: str = 'us-east-1') -> Dict:
    """Calculate costs for a specific resource type"""
    total_cost = 0.0
    resource_count = len(resources)
    
    if resource_type == 'ec2':
        for resource in resources:
            total_cost += estimate_ec2_cost(resource, region)
    elif resource_type == 'ebs':
        for resource in resources:
            total_cost += estimate_ebs_cost(resource, region)
    elif resource_type == 's3':
        for resource in resources:
            total_cost += estimate_s3_cost(resource)
    # IAM resources are free
    
    estimated_monthly = total_cost / resource_count if resource_count > 0 else 0.0
    
    return {
        'resourceType': resource_type,
        'currentCost': total_cost,
        'potentialSavings': total_cost,  # All unused resources are potential savings
        'estimatedMonthly': estimated_monthly,
        'resourceCount': resource_count
    }

@router.get("/cost-analysis")
async def get_cost_analysis(region: str = 'us-east-1'):
    """Get comprehensive cost analysis for all resources"""
    try:
        # Check cache first
        cache = get_cache()
        cache_key = f'cost_analysis_{region}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        aws_client = get_aws_client_factory()
        
        # Fetch all resource data directly using AWS clients
        factory = get_aws_client_factory()
        ec2_client = factory.session.client('ec2', region_name=region)
        s3_client = factory.session.client('s3')
        iam_client = factory.session.client('iam')
        
        # Get EC2 instances
        ec2_response = ec2_client.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
        )
        ec2_instances = []
        for reservation in ec2_response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                if 'User initiated' in instance.get('StateTransitionReason', ''):
                    ec2_instances.append({
                        'id': instance.get('InstanceId'),
                        'instance_type': instance.get('InstanceType', 't2.micro'),
                        'state': 'stopped'
                    })
        
        # Get EBS volumes
        ebs_response = ec2_client.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )
        ebs_volumes = []
        for volume in ebs_response.get('Volumes', []):
            ebs_volumes.append({
                'id': volume.get('VolumeId'),
                'size': volume.get('Size', 0),
                'state': 'available'
            })
        
        # Get S3 buckets (simplified - just count)
        try:
            s3_response = s3_client.list_buckets()
            s3_buckets = [{'name': bucket['Name'], 'size_gb': 10} for bucket in s3_response.get('Buckets', [])]
        except:
            s3_buckets = []
        
        # Get IAM roles (simplified)
        try:
            iam_paginator = iam_client.get_paginator('list_roles')
            iam_roles = []
            for page in iam_paginator.paginate():
                iam_roles.extend(page.get('Roles', []))
        except:
            iam_roles = []
        
        # Get IAM users (simplified)
        try:
            user_paginator = iam_client.get_paginator('list_users')
            iam_users = []
            for page in user_paginator.paginate():
                iam_users.extend(page.get('Users', []))
        except:
            iam_users = []
        
        # Access keys count (simplified)
        access_keys = []
        
        ec2_data = {'unused_instances': ec2_instances}
        ebs_data = {'unused_volumes': ebs_volumes}
        s3_data = {'unused_buckets': s3_buckets}
        iam_data = {'unused_roles': iam_roles}
        iam_users_data = {'unused_users': iam_users}
        access_keys_data = {'unused_keys': access_keys}
        
        # Calculate costs for each resource type
        estimates = []
        total_cost = 0.0
        total_resources = 0
        
        for resource_type, data_key, data in [
            ('ec2', 'unused_instances', ec2_data),
            ('ebs', 'unused_volumes', ebs_data),
            ('s3', 'unused_buckets', s3_data),
            ('iam', 'unused_roles', iam_data),
            ('iam_users', 'unused_users', iam_users_data),
            ('access_keys', 'unused_keys', access_keys_data)
        ]:
            resources = data.get(data_key, [])
            cost_info = calculate_resource_costs(resource_type, resources, region)
            estimates.append(cost_info)
            total_cost += cost_info['currentCost']
            total_resources += cost_info['resourceCount']
        
        # Try to get actual cost trends from Cost Explorer
        try:
            daily_costs = get_actual_costs_from_cost_explorer(days=7)
            trends = []
            
            if daily_costs:
                for date, cost in sorted(daily_costs.items()):
                    trends.append({
                        'date': date,
                        'totalCost': round(cost, 2),
                        'savings': round(total_cost * 0.1, 2),  # Estimated savings
                        'resourceCount': total_resources
                    })
            else:
                # Fallback to estimated trends
                for i in range(7):
                    date = datetime.now() - timedelta(days=6-i)
                    daily_cost = total_cost * (1.0 - (i * 0.05))
                    daily_savings = total_cost - daily_cost
                    trends.append({
                        'date': date.isoformat(),
                        'totalCost': round(daily_cost, 2),
                        'savings': round(daily_savings, 2),
                        'resourceCount': max(1, total_resources - i)
                    })
        except Exception as e:
            print(f"Error fetching Cost Explorer data: {e}")
            # Fallback to estimated trends
            trends = []
            for i in range(7):
                date = datetime.now() - timedelta(days=6-i)
                daily_cost = total_cost * (1.0 - (i * 0.05))
                daily_savings = total_cost - daily_cost
                trends.append({
                    'date': date.isoformat(),
                    'totalCost': round(daily_cost, 2),
                    'savings': round(daily_savings, 2),
                    'resourceCount': max(1, total_resources - i)
                })
        
        result = {
            'estimates': estimates,
            'trends': trends,
            'totalCurrentCost': round(total_cost, 2),
            'totalPotentialSavings': round(total_cost, 2),
            'totalResources': total_resources
        }
        
        # Cache for 1 hour
        from datetime import timedelta
        cache.set(cache_key, result, ttl=timedelta(hours=1))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cost analysis: {str(e)}")

@router.post("/cost-analysis/export/pdf")
async def export_cost_analysis_pdf(region: str = 'us-east-1'):
    """Export cost analysis as PDF using reportlab"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        
        # Get cost analysis data
        cost_data = await get_cost_analysis(region=region)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1  # Center
        )
        elements.append(Paragraph("Cloud Cleaner - Cost Analysis Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Metadata
        meta_style = styles['Normal']
        elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
        elements.append(Paragraph(f"<b>Region:</b> {region}", meta_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary Section
        summary_style = ParagraphStyle(
            'SummaryTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#059669'),
            spaceAfter=12
        )
        elements.append(Paragraph("Summary", summary_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Current Cost', f"${cost_data['totalCurrentCost']:.2f}/month"],
            ['Potential Savings', f"${cost_data['totalPotentialSavings']:.2f}/month"],
            ['Savings Percentage', f"{(cost_data['totalPotentialSavings']/cost_data['totalCurrentCost']*100) if cost_data['totalCurrentCost'] > 0 else 0:.1f}%"],
            ['Total Unused Resources', str(cost_data['totalResources'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Cost Breakdown Section
        elements.append(Paragraph("Cost Breakdown by Resource Type", summary_style))
        
        breakdown_data = [['Resource Type', 'Count', 'Monthly Cost', 'Potential Savings', 'Avg/Resource']]
        for estimate in cost_data['estimates']:
            if estimate['resourceCount'] > 0:  # Only show resources that exist
                breakdown_data.append([
                    estimate['resourceType'].upper(),
                    str(estimate['resourceCount']),
                    f"${estimate['currentCost']:.2f}",
                    f"${estimate['potentialSavings']:.2f}",
                    f"${estimate['estimatedMonthly']:.2f}"
                ])
        
        breakdown_table = Table(breakdown_data, colWidths=[1.5*inch, 0.8*inch, 1.2*inch, 1.3*inch, 1.2*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(breakdown_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1
        )
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Generated by Cloud Cleaner", footer_style))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=cost-analysis-{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
        
    except ImportError:
        # Fallback if reportlab is not installed
        raise HTTPException(
            status_code=500,
            detail="reportlab library not installed. Install with: pip install reportlab"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export PDF: {str(e)}")

@router.get("/cost-analysis/export/csv")
async def export_cost_analysis_csv(region: str = 'us-east-1'):
    """Export cost analysis as CSV"""
    try:
        # Get cost analysis data
        cost_data = await get_cost_analysis(region=region)
        
        # Generate CSV content
        csv_content = "Resource Type,Resource Count,Monthly Cost,Potential Savings,Avg Cost Per Resource\n"
        
        for estimate in cost_data['estimates']:
            csv_content += f"{estimate['resourceType']},{estimate['resourceCount']},${estimate['currentCost']:.2f},${estimate['potentialSavings']:.2f},${estimate['estimatedMonthly']:.2f}\n"
        
        csv_content += f"\nTotal,{cost_data['totalResources']},${cost_data['totalCurrentCost']:.2f},${cost_data['totalPotentialSavings']:.2f},-\n"
        
        # Create CSV response
        buffer = io.BytesIO(csv_content.encode('utf-8'))
        
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=cost-analysis-{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export CSV: {str(e)}")