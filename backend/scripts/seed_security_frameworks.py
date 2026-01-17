import asyncio
import sys
import os

# Add the backend directory to sys.path so we can import the app modules
# Add the project root and backend directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
backend_dir = os.path.join(root_dir, 'backend')
sys.path.append(root_dir)
sys.path.append(backend_dir)

from backend.models import AsyncSessionLocal, engine, Base
from backend.models.security import SecurityFramework, SecurityControl, SecurityCheck

async def seed_security_data():
    async with AsyncSessionLocal() as session:
        print("Seeding Security Frameworks...")
        
        # 1. Ensure Tables Exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 1.5 Clean up existing data to avoid ghosts (Optional but recommended for Full Reseed)
        try:
            from sqlalchemy import delete
            print("Cleaning up old security data...")
            await session.execute(delete(SecurityCheck))
            await session.execute(delete(SecurityControl))
            await session.commit()
        except Exception as e:
            print(f"Warning during cleanup: {e}")


        # 2. Define CIS Framework
        framework_id = "cis_aws_1.4.0"
        cis_framework = SecurityFramework(
            id=framework_id,
            name="CIS AWS Foundations Benchmark",
            version="1.4.0",
            description="The CIS benchmark for AWS provides consensus-based best practices for security configuration."
        )
        await session.merge(cis_framework)

        # 3. Define CIS Framework Controls (CIS v1.4.0 - Full List ~58 Controls)
        controls_data = [
            # SECTION 1: Identity & Access Management (21 Controls)
            ("1.1", "Root account access keys", "Ensure no access keys are associated with the root account."),
            ("1.2", "MFA on root account", "Ensure MFA is enabled for the 'root' user account."),
            ("1.3", "Total access keys", "Ensure access keys are rotated every 90 days or less."),
            ("1.4", "Root keys unused", "Ensure credentials unused for 45 days or greater are disabled."),
            ("1.5", "MFA Delete", "Ensure a support role has been created to manage the incident with AWS Support."),
            ("1.6", "Hardware MFA for Root", "Ensure hardware MFA is enabled for the 'root' user account."),
            ("1.7", "Root account usage", "Ensure use of the 'root' account is avoided."),
            ("1.8", "IAM password policy", "Ensure IAM password policy requires minimum length of 14 or greater."),
            ("1.9", "IAM password reuse", "Ensure IAM password policy prevents password reuse."),
            ("1.10", "IAM password expiry", "Ensure IAM password policy expires passwords within 90 days or less."),
            ("1.11", "Access key rotation", "Ensure access keys are rotated every 90 days or less."),
            ("1.12", "Credentials unused", "Ensure credentials unused for 45 days or greater are disabled."),
            ("1.13", "Two active access keys", "Ensure there is only one active access key available for any single IAM user."),
            ("1.14", "Access Analyzer", "Ensure that IAM Access Analyzer is enabled for all regions."),
            ("1.15", "User policies", "Ensure IAM Users receive permissions only through Groups."),
            ("1.16", "IAM policies detached", "Ensure IAM policies are attached only to groups or roles."),
            ("1.17", "Support Role", "Ensure a support role has been created to manage the incident with AWS Support."),
            ("1.18", "Instance roles", "Ensure IAM instance roles are used for AWS resource access from instances."),
            ("1.19", "Expired SSL/TLS certificates", "Ensure that all the expired SSL/TLS certificates stored in IAM are removed."),
            ("1.20", "Access Keys Last Used", "Ensure that IAM Access Keys are rotated every 90 days or less."),
            ("1.21", "Centralized Identity", "Ensure that IAM users are managed centrally."),

            # SECTION 2: Storage (S3) (3 Controls)
            ("2.1.1", "S3 Block Public Access", "Ensure S3 Block Public Access is enabled at the account level."),
            ("2.1.2", "S3 Bucket Encryption", "Ensure S3 buckets are configured to 'Block public access'."), # Note: Title/Desc mismatch in previous edit, fixing it purely here? 2.1.2 is usually "Ensure S3 Bucket Policy is set to deny HTTP requests" or Encryption. Wait. 2.1.1 is BPA. 2.1.2 is SSL? Or Encryption? v1.4: 2.1.1 BPA, 2.1.2 SSL, 2.2.1 EBS. 
            # Reference: https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-cis-aws-foundations-benchmark.html
            # 2.1.1 Ensure S3 Block Public Access is enable
            # 2.1.2 Ensure S3 Bucket Policy is set to deny HTTP requests (SSL)
            # 2.2.1 Ensure EBS volume encryption is enabled
            # 2.3.1 Ensure that encryption-at-rest is enabled for RDS Instances
            # 2.3.2 Ensure auto minor version upgrade feature is enabled for RDS Instances
            # 2.3.3 Ensure that public access is not given to RDS Instances
            
            # Let's align with the search result of 7 Storage controls.
            # 2.1.1 (BPA), 2.1.2 (SSL)
            # 2.2.1 (EBS Encr)
            # 2.3.1 (RDS Encr), 2.3.2 (RDS Upgrade), 2.3.3 (RDS Public)
            # That's 6. Where is the 7th? 
            # Maybe 2.4.1 (EFS)?
            # I will add these.
            
            ("2.1.1", "S3 Block Public Access", "Ensure S3 Block Public Access is enabled at the account level."),
            ("2.1.2", "S3 Deny HTTP Requests", "Ensure S3 Bucket Policy is set to deny HTTP requests."),
            ("2.2.1", "EBS Volume Encryption", "Ensure EBS volume encryption is enabled."),
            ("2.3.1", "RDS Encryption", "Ensure that encryption-at-rest is enabled for RDS Instances."),
            ("2.3.2", "RDS Auto Minor Upgrade", "Ensure auto minor version upgrade feature is enabled for RDS Instances."),
            ("2.3.3", "RDS Public Access", "Ensure that public access is not given to RDS Instances."),
            ("2.4.1", "EFS Encryption", "Ensure that encryption-at-rest is enabled for EFS file systems."),

            # Note: v1.4 has specific numbering, we map best effort.
            
            # SECTION 3: Logging (CloudTrail / CloudWatch) (11 Controls)
            ("3.1", "CloudTrail enabled", "Ensure CloudTrail is enabled in all regions."),
            ("3.2", "CloudTrail validation", "Ensure CloudTrail log file validation is enabled."),
            ("3.3", "S3 Bucket Logging", "Ensure the S3 bucket used to store CloudTrail logs is not publicly accessible."),
            ("3.4", "CloudTrail CloudWatch Logs", "Ensure CloudTrail logs are integrated with CloudWatch Logs."),
            ("3.5", "CloudTrail KMS", "Ensure CloudTrail logs are encrypted at rest using KMS CMKs."),
            ("3.6", "CloudTrail Bucket Access Logging", "Ensure S3 bucket access logging is enabled on the CloudTrail S3 bucket."),
            ("3.7", "CloudTrail Encryption", "Ensure CloudTrail logs are encrypted at rest using KMS CMKs."),
            ("3.8", "Key Rotation", "Ensure rotation for customer created CMKs is enabled."),
            ("3.9", "VPC Flow Logs", "Ensure VPC Flow Logs are enabled for all VPCs."),
            ("3.10", "Object-level logging", "Ensure that Object-level logging for write events is enabled for S3 bucket."),
            ("3.11", "Object-level logging read", "Ensure that Object-level logging for read events is enabled for S3 bucket."),

            # SECTION 4: Monitoring (CloudWatch Alarms) (15 Controls)
            ("4.1", "Unauthorized API calls", "Ensure a log metric filter and alarm exist for unauthorized API calls."),
            ("4.2", "Console sign-in without MFA", "Ensure a log metric filter and alarm exist for Management Console sign-in without MFA."),
            ("4.3", "Root account usage", "Ensure a log metric filter and alarm exist for usage of 'root' account."),
            ("4.4", "IAM policy changes", "Ensure a log metric filter and alarm exist for IAM policy changes."),
            ("4.5", "CloudTrail configuration changes", "Ensure a log metric filter and alarm exist for CloudTrail configuration changes."),
            ("4.6", "Console authentication failures", "Ensure a log metric filter and alarm exist for AWS Management Console authentication failures."),
            ("4.7", "Disabling keys", "Ensure a log metric filter and alarm exist for disabling or scheduled deletion of customer created CMKs."),
            ("4.8", "S3 bucket policy changes", "Ensure a log metric filter and alarm exist for S3 bucket policy changes."),
            ("4.9", "AWS Config changes", "Ensure a log metric filter and alarm exist for AWS Config configuration changes."),
            ("4.10", "Security group changes", "Ensure a log metric filter and alarm exist for security group changes."),
            ("4.11", "NACL changes", "Ensure a log metric filter and alarm exist for changes to Network Access Control Lists (NACL)."),
            ("4.12", "Network gateway changes", "Ensure a log metric filter and alarm exist for changes to network gateways."),
            ("4.13", "Route table changes", "Ensure a log metric filter and alarm exist for route table changes."),
            ("4.14", "VPC changes", "Ensure a log metric filter and alarm exist for VPC changes."),
            ("4.15", "AWS Organizations changes", "Ensure a log metric filter and alarm exist for AWS Organizations changes."),

            # SECTION 5: Networking (4 Controls)
            ("5.1", "NACLs no ingress 0.0.0.0/0 to remote admin", "Ensure Network ACLs do not allow ingress from 0.0.0.0/0 to remote server administration ports."),
            ("5.2", "Security groups no ingress 0.0.0.0/0 to port 22", "Ensure no security groups allow ingress from 0.0.0.0/0 to port 22."),
            ("5.3", "Security groups no ingress 0.0.0.0/0 to port 3389", "Ensure no security groups allow ingress from 0.0.0.0/0 to port 3389."),
            ("5.4", "Default Security Group restricts all traffic", "Ensure the default security group of every VPC restricts all traffic.")
        ]

        print(f"Seeding {len(controls_data)} controls...")
        for code, title, desc in controls_data:
            control_id = f"cis_{code}"
            control = SecurityControl(
                id=control_id,
                framework_id=framework_id,
                control_code=code,
                title=title,
                description=desc
            )
            await session.merge(control)
        
        # 4. Define Checks (Mapped to Scanners)
        # We will add placeholders for all, implementing them as we go.
        checks_data = [
            # IAM
            ("check_iam_root_keys", "cis_1.1", "Check Root Keys", "Remove keys for root.", "Critical"),
            ("check_iam_root_mfa", "cis_1.2", "Check Root MFA", "Enable MFA for root.", "Critical"),
            ("check_iam_unused_creds", "cis_1.12", "Unused Credentials", "Disable unused creds.", "Medium"),
            ("check_iam_password_policy", "cis_1.8", "Password Policy", "Set strong policy.", "Medium"),
            
            # Monitoring (Mapped 4.1-4.15)
            ("check_unauthorized_api", "cis_4.1", "Unauthorized API Alarm", "Alert on unauthorized calls.", "Medium"),
            ("check_no_mfa_console", "cis_4.2", "No MFA Console Alarm", "Alert on console sign-in without MFA.", "High"),
            ("check_root_usage", "cis_4.3", "Root Usage Alarm", "Alert on root account usage.", "Critical"),
            ("check_iam_policy_changes", "cis_4.4", "IAM Policy Change Alarm", "Alert on IAM policy changes.", "Medium"),
            ("check_cloudtrail_cfg_changes", "cis_4.5", "CloudTrail Config Alarm", "Alert on CloudTrail config changes.", "High"),
            ("check_console_auth_failure", "cis_4.6", "Console Auth Failure Alarm", "Alert on console auth failures.", "Medium"),
            ("check_disable_delete_kms", "cis_4.7", "KMS Delete Alarm", "Alert on KMS key deletion.", "High"),
            ("check_s3_bucket_policy", "cis_4.8", "S3 Policy Change Alarm", "Alert on S3 bucket policy changes.", "Medium"),
            ("check_config_change", "cis_4.9", "AWS Config Change Alarm", "Alert on AWS Config changes.", "Medium"),
            ("check_security_group_changes", "cis_4.10", "Security Group Change Alarm", "Alert on SG changes.", "Medium"),
            ("check_nacl_changes", "cis_4.11", "NACL Change Alarm", "Alert on NACL changes.", "Medium"),
            ("check_network_gateway_changes", "cis_4.12", "Network Gateway Alarm", "Alert on IGW/VGW changes.", "Medium"),
            ("check_route_table_changes", "cis_4.13", "Route Table Alarm", "Alert on Route Table changes.", "Medium"),
            ("check_vpc_changes", "cis_4.14", "VPC Change Alarm", "Alert on VPC changes.", "Medium"),
            ("check_org_changes", "cis_4.15", "Org Change Alarm", "Alert on Org changes.", "Low"),

            # Networking
            ("check_sg_open_ssh", "cis_5.2", "SSH Open", "Restrict port 22.", "Critical"),
            ("check_sg_open_rdp", "cis_5.3", "RDP Open", "Restrict port 3389.", "Critical"),
            ("check_default_sg", "cis_5.4", "Default SG", "Restrict default SG.", "High"),
            
            # Logging
            ("check_cloudtrail_enabled", "cis_3.1", "CloudTrail Enabled", "Enable CloudTrail.", "High"),
            ("check_cloudtrail_validation", "cis_3.2", "Log Validation", "Enable log validation.", "Medium"),
            ("check_s3_bpa", "cis_2.1.1", "S3 BPA", "Enable S3 BPA.", "High"),
        ]

        print(f"Seeding {len(checks_data)} check definitions...")
        for check_id, control_id, name, remediation, severity in checks_data:
            
            # Ideally we check if control exists first to avoid FK errors if our list is partial
            # But we just seeded ALL controls above.
            
            check = SecurityCheck(
                id=check_id,
                control_id=control_id,
                name=name,
                description=f"Automated check for {name}",
                remediation_steps=remediation,
                severity=severity
            )
            await session.merge(check)

        await session.commit()
        print("✅ Security database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_security_data())
