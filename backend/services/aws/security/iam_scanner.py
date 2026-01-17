from typing import List, Dict, Any
import logging
from .base import SecurityScannerBase
from models.security import FindingStatus
import datetime
from dateutil.parser import parse

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

            # New check: Unused credentials
            credential_report = self._get_credential_report(iam_client)
            if credential_report:
                unused_credentials_finding = self._check_unused_credentials(credential_report)
                if unused_credentials_finding:
                    findings.append(unused_credentials_finding)

        except Exception as e:
            logger.error(f"Error running IAM security checks: {e}")
            
        return findings

    def _get_credential_report(self, client) -> List[Dict[str, Any]]:
        """
        Fetches the IAM credential report.
        """
        try:
            # Generate report
            client.generate_credential_report()
            
            # Wait for report to be ready
            report_state = ''
            max_retries = 10
            retries = 0
            while report_state != 'COMPLETE' and retries < max_retries:
                response = client.get_credential_report()
                report_state = response.get('ReportState')
                if report_state == 'COMPLETE':
                    break
                elif report_state == 'STARTED':
                    # Wait a bit before retrying
                    import time
                    time.sleep(1)
                    retries += 1
                else:
                    logger.warning(f"Credential report generation failed or unknown state: {report_state}")
                    return []

            if report_state != 'COMPLETE':
                return []

            response = client.get_credential_report()
            report_content = response.get('Content').decode('utf-8')
            import csv
            import io
            reader = csv.DictReader(io.StringIO(report_content))
            return list(reader)
        except Exception as e:
            logger.error(f"Failed to get credential report: {e}")
            return []

    def _check_root_access_keys(self, client) -> Dict[str, Any]:
        """
        CIS 1.1: Ensure no access keys are associated with the root account.
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

    def _check_unused_credentials(self, credential_report: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        CIS 1.16: Ensure IAM users' credentials are disabled if unused for 45 days.
        """
        try:
            unused_users = []
            now = datetime.datetime.now(datetime.timezone.utc)
            cutoff_days = 45

            for row in credential_report:
                user = row['user']
                if user == '<root_account>':
                    continue

                # Check Password Last Used
                password_enabled = row.get('password_enabled') == 'true'
                password_last_used = row.get('password_last_used')
                
                # Check Access Key 1
                ak1_active = row.get('access_key_1_active') == 'true'
                ak1_last_used = row.get('access_key_1_last_used_date')

                # Check Access Key 2
                ak2_active = row.get('access_key_2_active') == 'true'
                ak2_last_used = row.get('access_key_2_last_used_date')

                issues = []
                
                # Check Password
                if password_enabled and password_last_used != 'no_information':
                    try:
                        last_used_dt = parse(password_last_used)
                        if (now - last_used_dt).days > cutoff_days:
                            issues.append(f"Password unused for {(now - last_used_dt).days} days")
                    except: pass
                elif password_enabled and password_last_used == 'no_information':
                     # If enabled but never used? technically unused.
                     pass

                # Check Keys
                if ak1_active and ak1_last_used != 'N/A':
                    try:
                        last_used_dt = parse(ak1_last_used)
                        if (now - last_used_dt).days > cutoff_days:
                             issues.append(f"Access Key 1 unused for {(now - last_used_dt).days} days")
                    except: pass
                
                if ak2_active and ak2_last_used != 'N/A':
                     try:
                        last_used_dt = parse(ak2_last_used)
                        if (now - last_used_dt).days > cutoff_days:
                             issues.append(f"Access Key 2 unused for {(now - last_used_dt).days} days")
                     except: pass
                
                if issues:
                    unused_users.append({
                        "user": user,
                        "issues": issues
                    })

            status = FindingStatus.FAIL if unused_users else FindingStatus.PASS
            evidence = {
                "unused_stats": f"{len(unused_users)} users with unused credentials",
                "details": unused_users[:10] # Cap evidence size
            }

            return self.build_finding(
                check_id="check_iam_unused_creds",
                status=status,
                resource_id="iam-users",
                resource_type="AWS::IAM::User",
                evidence=evidence
            )
            
        except Exception as e:
            logger.warning(f"Failed check 1.16: {e}")
            return None
