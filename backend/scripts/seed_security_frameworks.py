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
        
        # 1. Ensure Tables Exist (if not using Alembic/Migrations yet)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 2. Define CIS Framework
        framework_id = "cis_aws_1.4.0"
        cis_framework = SecurityFramework(
            id=framework_id,
            name="CIS AWS Foundations Benchmark",
            version="1.4.0",
            description="The CIS benchmark for AWS provides consensus-based best practices for security configuration."
        )
        await session.merge(cis_framework)

        # 3. Define MVP Controls
        controls_data = [
            ("1.1", "Root account access keys disabled", "Ensure no access keys are associated with the root account."),
            ("1.2", "MFA enabled on root account", "Ensure MFA is enabled for the 'root' user account."),
            ("1.3", "IAM password policy enforced", "Ensure the credentials of all IAM users adhere to a strong password policy."),
            ("2.1", "CloudTrail enabled in all regions", "Ensure CloudTrail is enabled in all regions."),
            ("2.3", "S3 Bucket CloudTrail logs access logging", "Ensure S3 bucket access logging is enabled on the CloudTrail S3 bucket."),
            ("2.4", "CloudTrail logs integrated with CloudWatch", "Ensure CloudTrail logs are integrated with CloudWatch Logs."),
            ("3.3", "S3 Bucket Public Access via Policy", "Ensure S3 buckets do not allow public read access via S3 policy."),
            ("3.4", "S3 Bucket Public Access via ACL", "Ensure S3 buckets do not allow public read access via ACLs."),
            ("4.2", "Restricted Access to Port 22", "Ensure no security groups allow ingress from 0.0.0.0/0 to port 22."),
            ("5.2", "Restricted Access to Port 3389", "Ensure no security groups allow ingress from 0.0.0.0/0 to port 3389."),
            ("4.4", "Default Security Group restricts all traffic", "Ensure the default security group of every VPC restricts all traffic."),
            ("4.3", "Log metric filter and alarm for root usage", "Ensure a log metric filter and alarm exist for usage of 'root' account."),
            ("5.1", "NACLs no ingress 0.0.0.0/0 to remote admin", "Ensure Network ACLs do not allow ingress from 0.0.0.0/0 to remote server administration ports."),
            ("3.5", "Enable VPC Flow Logs", "Ensure VPC Flow Logs are enabled for all VPCs."),
            ("1.16", "Unused IAM Credentials", "Ensure credentials unused for 45 days or greater are disabled."),
            ("3.6", "S3 Bucket Access Logging", "Ensure S3 bucket access logging is enabled on the CloudTrail S3 bucket."),
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
        checks_data = [
            # ID, Control ID, Name, Remediation, Severity
            ("check_iam_root_keys", "cis_1.1", "Check Root Keys", "Remove keys for root.", "Critical"),
            ("check_iam_root_mfa", "cis_1.2", "Check Root MFA", "Enable MFA for root.", "Critical"),
            ("check_iam_password_policy", "cis_1.3", "Check Password Policy", "Set a strong policy.", "Medium"),
            ("check_cloudtrail_enabled", "cis_2.1", "Check CloudTrail", "Enable CloudTrail.", "High"),
            ("check_cloudtrail_validation", "cis_2.2", "CloudTrail Log Validation", "Enable log file validation.", "Medium"),
            ("check_s3_block_public", "cis_3.1", "Check S3 BPA", "Turn on BPA.", "High"),
            ("check_s3_encryption", "cis_3.2", "Check S3 Encryption", "Enable Bucket Encryption.", "High"),
            ("check_sg_open_ports", "cis_4.1", "Check Open Ports", "Restrict 0.0.0.0/0 on port 22/3389.", "Critical"),
            ("check_default_sg_restricted", "cis_4.4", "Check Default SG", "Remove rules from default SG.", "High"),
            ("check_root_usage_alarm", "cis_4.3", "Root Usage Alarm", "Create metric filter/alarm for Root usage.", "Medium"),
            ("check_vpc_flow_logs", "cis_3.5", "VPC Flow Logs", "Ensure VPC Flow Logs are enabled for all VPCs.", "Medium"),
            ("check_iam_unused_creds", "cis_1.16", "Unused IAM Credentials", "Ensure credentials unused for 45+ days are disabled.", "Medium"),
            ("check_s3_logging", "cis_3.6", "S3 Bucket Logging", "Ensure S3 bucket access logging is enabled.", "Medium"),
        ]

        print(f"Seeding {len(checks_data)} check definitions...")
        for check_id, control_id, name, remediation, severity in checks_data:
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
