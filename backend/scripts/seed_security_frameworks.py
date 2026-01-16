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
            ("2.2", "CloudTrail log file validation", "Ensure CloudTrail log file validation is enabled."),
            ("3.1", "S3 Block Public Access enabled", "Ensure S3 Block Public Access is enabled at the account level."),
            ("3.2", "S3 encryption enabled", "Ensure Server-Side Encryption is enabled for all S3 buckets."),
            ("4.1", "Security groups restrict 0.0.0.0/0", "Ensure no security groups allow ingress from 0.0.0.0/0 to remote server administration ports.")
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
        
        # 4. Define Placeholder Checks (Phase 1 will implement these)
        # We pre-seed them so the dashboard isn't empty.
        checks_data = [
            ("check_iam_root_keys", "cis_1.1", "Check Root Keys", "Remove keys for root.", "Critical"),
            ("check_iam_root_mfa", "cis_1.2", "Check Root MFA", "Enable MFA for root.", "Critical"),
            ("check_iam_password_policy", "cis_1.3", "Check Password Policy", "Set a strong policy.", "Medium"),
            ("check_cloudtrail_enabled", "cis_2.1", "Check CloudTrail", "Enable CloudTrail.", "High"),
            ("check_s3_block_public", "cis_3.1", "Check S3 BPA", "Turn on BPA.", "High"),
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
