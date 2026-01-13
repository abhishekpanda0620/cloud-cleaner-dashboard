"""
Scanner Registry for managing AWS service scanners.

This module provides a registry system that:
1. Discovers available scanner plugins
2. Maps service codes to scanners
3. Provides fallback to generic scanner
4. Handles scanner loading and initialization
"""

import logging
from typing import Dict, List, Optional, Type
from pathlib import Path
import importlib
import inspect

from .scanner_base import ScannerBase, GenericScanner

logger = logging.getLogger(__name__)


class ScannerRegistry:
    """
    Registry for AWS service scanners.
    
    This class manages the discovery and loading of scanner plugins.
    It automatically discovers scanners in the scanners/ directory
    and provides a fallback to GenericScanner for unknown services.
    """
    
    def __init__(self):
        """Initialize the scanner registry."""
        self._scanners: Dict[str, Type[ScannerBase]] = {}
        self._loaded = False
        
    def load_scanners(self) -> None:
        """
        Discover and load all available scanner plugins.
        
        This method scans the scanners/ directory for scanner classes
        and registers them by their service_code.
        """
        if self._loaded:
            return
            
        try:
            # Get the scanners directory path
            scanners_dir = Path(__file__).parent / 'scanners'
            
            if not scanners_dir.exists():
                logger.warning(f"Scanners directory not found: {scanners_dir}")
                self._loaded = True
                return
            
            # Iterate through Python files in scanners directory
            for scanner_file in scanners_dir.glob('*.py'):
                if scanner_file.name.startswith('_'):
                    continue
                    
                try:
                    # Import the module
                    module_name = f'services.aws.scanners.{scanner_file.stem}'
                    # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
                    module = importlib.import_module(module_name)
                    
                    # Find scanner classes in the module
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Check if it's a scanner class (inherits from ScannerBase)
                        if (issubclass(obj, ScannerBase) and 
                            obj is not ScannerBase and 
                            obj is not GenericScanner):
                            
                            # Instantiate to get service_code
                            try:
                                scanner_instance = obj()
                                service_code = scanner_instance.service_code
                                self._scanners[service_code] = obj
                                logger.info(f"Registered scanner: {name} for {service_code}")
                            except Exception as e:
                                logger.warning(f"Could not instantiate scanner {name}: {e}")
                                
                except Exception as e:
                    logger.warning(f"Could not load scanner from {scanner_file}: {e}")
                    
            logger.info(f"Loaded {len(self._scanners)} scanner(s)")
            self._loaded = True
            
        except Exception as e:
            logger.error(f"Error loading scanners: {e}")
            self._loaded = True
    
    def get_scanner(
        self,
        service_code: str,
        service_name: str,
        region: str = 'us-east-1'
    ) -> ScannerBase:
        """
        Get scanner for a service.
        
        If a specific scanner exists, return it.
        Otherwise, return a GenericScanner as fallback.
        
        Args:
            service_code: AWS service code (e.g., 'AmazonEC2')
            service_name: Human-readable service name
            region: AWS region
            
        Returns:
            Scanner instance (specific or generic)
        """
        # Ensure scanners are loaded
        if not self._loaded:
            self.load_scanners()
        
        # Check if specific scanner exists
        if service_code in self._scanners:
            logger.debug(f"Using specific scanner for {service_code}")
            return self._scanners[service_code](region=region)
        
        # Fallback to generic scanner
        logger.debug(f"Using generic scanner for {service_code}")
        return GenericScanner(
            service_code=service_code,
            service_name=service_name,
            region=region
        )
    
    def has_scanner(self, service_code: str) -> bool:
        """
        Check if a specific scanner exists for a service.
        
        Args:
            service_code: AWS service code
            
        Returns:
            True if specific scanner exists, False otherwise
        """
        if not self._loaded:
            self.load_scanners()
        return service_code in self._scanners
    
    def list_scanners(self) -> List[Dict[str, str]]:
        """
        List all registered scanners.
        
        Returns:
            List of scanner information dicts
        """
        if not self._loaded:
            self.load_scanners()
        
        scanners = []
        for service_code, scanner_class in self._scanners.items():
            try:
                scanner = scanner_class()
                scanners.append({
                    'service_code': service_code,
                    'service_name': scanner.service_name,
                    'service_category': scanner.service_category,
                    'scanner_class': scanner_class.__name__
                })
            except Exception as e:
                logger.warning(f"Could not get info for scanner {scanner_class}: {e}")
        
        return scanners
    
    def get_scanner_count(self) -> int:
        """
        Get number of registered scanners.
        
        Returns:
            Number of specific scanners available
        """
        if not self._loaded:
            self.load_scanners()
        return len(self._scanners)


# Global registry instance
_registry = ScannerRegistry()


def get_scanner_registry() -> ScannerRegistry:
    """
    Get the global scanner registry instance.
    
    Returns:
        ScannerRegistry instance
    """
    return _registry


def get_scanner(
    service_code: str,
    service_name: str,
    region: str = 'us-east-1'
) -> ScannerBase:
    """
    Convenience function to get a scanner from the global registry.
    
    Args:
        service_code: AWS service code
        service_name: Human-readable service name
        region: AWS region
        
    Returns:
        Scanner instance
    """
    return _registry.get_scanner(service_code, service_name, region)