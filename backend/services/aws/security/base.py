from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
from core.aws_client import get_aws_client_factory
# Note: We import FindingStatus to use strict enums, but methods return simple Dicts
# that will be mapped to the DB model later by the orchestrator.
from models.security import FindingStatus

logger = logging.getLogger(__name__)

class SecurityScannerBase(ABC):
    """
    Abstract base class for AWS Security Scanners.
    Each implementation (e.g., IAMScanner, S3Scanner) is responsible for
    executing a specific set of compliance checks (CIS, etc.).
    """
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.factory = get_aws_client_factory()
        self.session = self.factory.session
        self.account_id = self._get_account_id()

    def _get_account_id(self) -> str:
        try:
            return self.session.client('sts').get_caller_identity().get('Account')
        except Exception as e:
            logger.error(f"Failed to get account ID: {e}")
            return "unknown"

    @property
    @abstractmethod
    def service_name(self) -> str:
        """Name of the service being scanned (e.g. 'IAM', 'S3')"""
        pass

    @abstractmethod
    def run_checks(self) -> List[Dict[str, Any]]:
        """
        Execute all checks.
        Returns a list of finding dictionaries:
        {
            "check_id": "check_iam_root_mfa",
            "status": "PASS" | "FAIL",
            "resource_id": "root",
            "resource_type": "AWS::IAM::User",
            "region": "global",
            "account_id": "123456789012",
            "evidence": {"detail": "..."}
        }
        """
        pass

    def build_finding(self, check_id: str, status: FindingStatus, 
                      resource_id: str, resource_type: str, 
                      evidence: Dict[str, Any], region: str = None) -> Dict[str, Any]:
        """Helper to construct a standardized finding dictionary"""
        return {
            "check_id": check_id,
            "status": status.value,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "region": region or self.region,
            "account_id": self.account_id,
            "evidence": evidence
        }
