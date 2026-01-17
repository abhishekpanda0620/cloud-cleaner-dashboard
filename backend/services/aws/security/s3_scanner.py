from typing import List, Dict, Any
import logging
from .base import SecurityScannerBase
from models.security import FindingStatus

logger = logging.getLogger(__name__)

class S3SecurityScanner(SecurityScannerBase):
    
    @property
    def service_name(self) -> str:
        return "S3"

    def run_checks(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            s3_client = self.session.client('s3', region_name=self.region)
            
            # CIS 3.1 Ensure S3 Block Public Access is enabled at the account level
            findings.append(self._check_account_public_access_block(s3_client))

            # CIS 3.2 Ensure Server-Side Encryption is enabled for all S3 buckets
            findings.extend(self._check_bucket_encryption(s3_client))
            
            # CIS 3.6 Ensure S3 bucket access logging is enabled
            findings.extend(self._check_bucket_logging(s3_client))
            
        except Exception as e:
            logger.error(f"Error running S3 security checks: {e}")
            
        return [f for f in findings if f]

    def _check_account_public_access_block(self, client) -> Dict[str, Any]:
        """
        CIS 3.1: Ensure S3 Block Public Access is enabled at the account level.
        """
        try:
            s3control = self.session.client('s3control', region_name=self.region)
            
            response = s3control.get_public_access_block(AccountId=self.account_id)
            config = response.get('PublicAccessBlockConfiguration', {})
            
            # Require all 4 to be True for compliance
            block_public_acls = config.get('BlockPublicAcls', False)
            ignore_public_acls = config.get('IgnorePublicAcls', False)
            block_public_policy = config.get('BlockPublicPolicy', False)
            restrict_public_buckets = config.get('RestrictPublicBuckets', False)
            
            is_compliant = all([block_public_acls, ignore_public_acls, block_public_policy, restrict_public_buckets])
            status = FindingStatus.PASS if is_compliant else FindingStatus.FAIL
            
            return self.build_finding(
                check_id="check_s3_block_public",
                status=status,
                resource_id=f"account-{self.account_id}",
                resource_type="AWS::S3::Account",
                evidence={
                    "BlockPublicAcls": block_public_acls,
                    "IgnorePublicAcls": ignore_public_acls,
                    "BlockPublicPolicy": block_public_policy,
                    "RestrictPublicBuckets": restrict_public_buckets
                }
            )

        except Exception as e:
            # If no configuration exists, it usually throws a 404/NoSuchPublicAccessBlockConfiguration
            # Which is a FAIL.
            if "NoSuchPublicAccessBlockConfiguration" in str(e):
                 return self.build_finding(
                    check_id="check_s3_block_public",
                    status=FindingStatus.FAIL,
                    resource_id=f"account-{self.account_id}",
                    resource_type="AWS::S3::Account",
                    evidence={"error": "No Public Access Block configuration found"}
                )
            return None

    def _check_bucket_encryption(self, client) -> List[Dict[str, Any]]:
        """
        CIS 3.2: Ensure Server-Side Encryption is enabled for all S3 buckets.
        """
        findings = []
        try:
            # List all buckets
            response = client.list_buckets()
            buckets = response.get('Buckets', [])
            
            for bucket in buckets:
                name = bucket['Name']
                try:
                    # Check encryption
                    enc_resp = client.get_bucket_encryption(Bucket=name)
                    rules = enc_resp.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
                    
                    is_encrypted = False
                    for rule in rules:
                        status = rule.get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm')
                        if status:
                            is_encrypted = True
                            break
                    
                    if is_encrypted:
                         findings.append(self.build_finding(
                            check_id="check_s3_encryption",
                            status=FindingStatus.PASS,
                            resource_id=name,
                            resource_type="AWS::S3::Bucket",
                            evidence={"encryption": "Enabled"}
                        ))
                    
                except client.exceptions.ClientError as e:
                    # If encryption is not enabled, it throws ServerSideEncryptionConfigurationNotFoundError
                    if "ServerSideEncryptionConfigurationNotFoundError" in str(e):
                        findings.append(self.build_finding(
                            check_id="check_s3_encryption",
                            status=FindingStatus.FAIL,
                            resource_id=name,
                            resource_type="AWS::S3::Bucket",
                            evidence={"error": "Server Side Encryption not enabled"}
                        ))
                    else:
                        logger.debug(f"Could not check encryption for {name}: {e}")

        except Exception as e:
            logger.warning(f"Failed check 3.2: {e}")
            
        return findings

    def _check_bucket_logging(self, client) -> List[Dict[str, Any]]:
        """
        CIS 3.6: Ensure S3 bucket access logging is enabled.
        """
        findings = []
        try:
            response = client.list_buckets()
            buckets = response.get('Buckets', [])

            for bucket in buckets:
                name = bucket['Name']
                try:
                    logging_resp = client.get_bucket_logging(Bucket=name)
                    logging_enabled = 'LoggingEnabled' in logging_resp
                    
                    if logging_enabled:
                         findings.append(self.build_finding(
                            check_id="check_s3_logging",
                            status=FindingStatus.PASS,
                            resource_id=name,
                            resource_type="AWS::S3::Bucket",
                            evidence={"target_bucket": logging_resp['LoggingEnabled']['TargetBucket']}
                        ))
                    else:
                        findings.append(self.build_finding(
                            check_id="check_s3_logging",
                            status=FindingStatus.FAIL,
                            resource_id=name,
                            resource_type="AWS::S3::Bucket",
                            evidence={"error": "Access logging not enabled"}
                        ))

                except Exception as e:
                    logger.debug(f"Could not check logging for {name}: {e}")

        except Exception as e:
             logger.warning(f"Failed check 3.6: {e}")
        
        return findings
