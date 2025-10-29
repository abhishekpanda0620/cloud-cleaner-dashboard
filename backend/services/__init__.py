"""
Services module for multi-cloud resource discovery and management.

Structure:
- aws/ - AWS-specific services (Config, Cost Explorer, etc.)
- azure/ - Azure-specific services (future)
- gcp/ - GCP-specific services (future)
- base/ - Base classes and interfaces for all cloud providers
"""

from .aws.config_client import AWSConfigClient
from .aws.cost_explorer import CostExplorerClient
from .aws.discovery import AWSServiceDiscoveryEngine

__all__ = [
    'AWSConfigClient',
    'CostExplorerClient',
    'AWSServiceDiscoveryEngine',
]