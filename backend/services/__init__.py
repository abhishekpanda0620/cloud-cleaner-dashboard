"""
Services module for multi-cloud resource discovery and management.

Structure:
- aws/ - AWS-specific services (Scanner system, Cost Explorer, etc.)
- azure/ - Azure-specific services (future)
- gcp/ - GCP-specific services (future)
- base/ - Base classes and interfaces for all cloud providers
"""

from .aws.cost_explorer import CostExplorerClient
from .aws.discovery import AWSServiceDiscoveryEngine
from .aws.scanner_registry import get_scanner_registry

__all__ = [
    'CostExplorerClient',
    'AWSServiceDiscoveryEngine',
    'get_scanner_registry',
]