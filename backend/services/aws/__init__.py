"""
AWS-specific services for resource discovery and cost analysis.

This module provides:
- AWS Config integration for resource discovery
- AWS Cost Explorer integration for cost tracking  
- Service discovery engine for AWS
"""

from .config_client import AWSConfigClient
from .cost_explorer import CostExplorerClient
from .discovery import AWSServiceDiscoveryEngine

__all__ = [
    'AWSConfigClient',
    'CostExplorerClient',
    'AWSServiceDiscoveryEngine',
]