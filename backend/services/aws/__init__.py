"""
AWS-specific services for resource discovery and cost analysis.

This module provides:
- Scanner-based resource discovery
- AWS Cost Explorer integration for cost tracking
- Service discovery engine for AWS
"""

from .cost_explorer import CostExplorerClient
from .discovery import AWSServiceDiscoveryEngine
from .scanner_registry import get_scanner_registry

__all__ = [
    'CostExplorerClient',
    'AWSServiceDiscoveryEngine',
    'get_scanner_registry',
]