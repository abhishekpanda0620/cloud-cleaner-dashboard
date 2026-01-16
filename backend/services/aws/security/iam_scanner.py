from typing import List, Dict, Any
import logging
from .base import SecurityScannerBase
from models.security import FindingStatus

logger = logging.getLogger(__name__)

class IAMSecurityScanner(SecurityScannerBase):
    
    @property
    def service_name(self) -> str:
        return "IAM"

    def run_checks(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            iam_client = self.session.client('iam', region_name='us-east-1') # IAM is global
            
            # Check 1.1 & 1.2: Root Account Checks (Requires Credential Report)
            # Generating a credential report can take time, so often tools skip this or wait.
            # For this MVP, we will try to get the summary or just check Account Summary first.
            
            # CIS 1.1 Avoid the use of the "root" account
            # This is hard to check via API (requires CloudTrail analysis usually), but we can check if Access Keys exist.
            root_keys_finding = self._check_root_access_keys(iam_client)
            if root_keys_finding:
                findings.append(root_keys_finding)

            # CIS 1.2 Enable MFA for the "root" account
            # We can check account summary for 'AccountMFAEnabled'
            mfa_finding = self._check_root_mfa(iam_client)
            if mfa_finding:
                findings.append(mfa_finding)
            
            # CIS 1.3 Enable password policy
            policy_finding = self._check_password_policy(iam_client)
            if policy_finding:
                findings.append(policy_finding)

        except Exception as e:
            logger.error(f"Error running IAM security checks: {e}")
            
        return findings

    def _check_root_access_keys(self, client) -> Dict[str, Any]:
        """
        CIS 1.1: Ensure no access keys are associated with the root account.
        Strategy: Use get_account_summary() -> AccountAccessKeysPresent?
        Actually, get_account_summary gives total keys, but we want ROOT keys.
        The most reliable way is `get_credential_report`, but that's async and slow.
        
        Alternative: `get_account_summary` returns `AccountAccessKeysPresent`. 
        Note: This field indicates if there are *any* access keys for the ACCOUNT (usually root).
        Wait, `AccountAccessKeysPresent` in get_account_summary traditionally refers to the root account's keys?
        Let's verify: AWS docs say "The number of access keys for the AWS account root user." (Map content usually).
        """
        try:
            summary = client.get_account_summary()
            summary_map = summary.get('SummaryMap', {})
            
            root_access_keys = summary_map.get('AccountAccessKeysPresent', 0)
            
            status = FindingStatus.FAIL if root_access_keys > 0 else FindingStatus.PASS
            
            return self.build_finding(
                check_id="check_iam_root_keys",
                status=status,
                resource_id="root",
                resource_type="AWS::IAM::User",
                evidence={"AccountAccessKeysPresent": root_access_keys}
            )
        except Exception as e:
            logger.warning(f"Failed check 1.1: {e}")
            return None

    def _check_root_mfa(self, client) -> Dict[str, Any]:
        """
        CIS 1.2: Ensure MFA is enabled for the 'root' user account.
        Strategy: get_account_summary() -> AccountMFAEnabled
        """
        try:
            summary = client.get_account_summary()
            summary_map = summary.get('SummaryMap', {})
            
            mfa_enabled = summary_map.get('AccountMFAEnabled', 0)
            
            # Note: AccountMFAEnabled is an integer (1 if enabled, 0 if not)
            status = FindingStatus.PASS if mfa_enabled == 1 else FindingStatus.FAIL
            
            return self.build_finding(
                check_id="check_iam_root_mfa",
                status=status,
                resource_id="root",
                resource_type="AWS::IAM::User",
                evidence={"AccountMFAEnabled": mfa_enabled}
            )
        except Exception as e:
            logger.warning(f"Failed check 1.2: {e}")
            return None

    def _check_password_policy(self, client) -> Dict[str, Any]:
        """
        CIS 1.3: Enforce password policy.
        """
        try:
            try:
                response = client.get_account_password_policy()
                policy = response.get('PasswordPolicy', {})
                
                # Compliance logic:
                # 1. RequireUppercaseCharacters
                # 2. RequireLowercaseCharacters
                # 3. RequireSymbols
                # 4. RequireNumbers
                # 5. MinimumPasswordLength >= 14
                
                length = policy.get('MinimumPasswordLength', 0)
                upper = policy.get('RequireUppercaseCharacters', False)
                lower = policy.get('RequireLowercaseCharacters', False)
                symbol = policy.get('RequireSymbols', False)
                number = policy.get('RequireNumbers', False)
                
                is_passing = (length >= 14 and upper and lower and symbol and number)
                
                status = FindingStatus.PASS if is_passing else FindingStatus.FAIL
                
                evidence = {
                    "MinimumPasswordLength": length,
                    "RequireUppercase": upper,
                    "RequireLowercase": lower,
                    "RequireSymbols": symbol,
                    "RequireNumbers": number
                }
                
            except client.exceptions.NoSuchEntityException:
                # No password policy set
                status = FindingStatus.FAIL
                evidence = {"error": "No password policy found"}
            
            return self.build_finding(
                check_id="check_iam_password_policy",
                status=status,
                resource_id="password-policy",
                resource_type="AWS::IAM::Policy",
                evidence=evidence
            )
        except Exception as e:
            logger.warning(f"Failed check 1.3: {e}")
            return None
