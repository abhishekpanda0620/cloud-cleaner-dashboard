
import pytest
from services.aws.scanner_registry import ScannerRegistry, GenericScanner, get_scanner_registry
from services.aws.scanner_base import ScannerBase

class MockScanner(ScannerBase):
    @property
    def service_name(self):
        return "Mock Service"
    
    @property
    def service_code(self):
        return "mock_service"
    
    @property
    def service_category(self):
        return "Other"
        
    def scan(self, regions=None):
        return []
        
    def identify_unused(self, resource):
        return False

def test_registry_singleton_accessor():
    """Test that get_scanner_registry returns a singleton-like instance"""
    registry1 = get_scanner_registry()
    registry2 = get_scanner_registry()
    assert registry1 is registry2

def test_get_specific_scanner():
    """Test retrieving a specific scanner"""
    registry = ScannerRegistry()
    # Manually inject mock scanner since there is no public register method
    # and we don't want to rely on file discovery for unit tests
    registry._scanners["mock_service"] = MockScanner
    registry._loaded = True
    
    # args: service_code, service_name
    scanner = registry.get_scanner("mock_service", "Mock Service")
    assert isinstance(scanner, MockScanner)

def test_get_generic_scanner_fallback():
    """Test fallback to GenericScanner"""
    registry = ScannerRegistry()
    registry._loaded = True # Prevent auto-loading
    
    scanner = registry.get_scanner("unknown_service", "Unknown Service")
    assert isinstance(scanner, GenericScanner)
    assert scanner.service_code == "unknown_service"

def test_list_scanners():
    """Test listing scanners"""
    registry = ScannerRegistry()
    registry._scanners["mock_service"] = MockScanner
    registry._loaded = True
    
    scanners = registry.list_scanners()
    assert len(scanners) == 1
    assert scanners[0]['service_code'] == "mock_service"
    assert scanners[0]['service_name'] == "Mock Service"
