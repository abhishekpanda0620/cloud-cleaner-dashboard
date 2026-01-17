import asyncio
import os
import sys

# Setup path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
backend_dir = os.path.join(root_dir, 'backend')
sys.path.append(root_dir)
sys.path.append(backend_dir)

from backend.models import AsyncSessionLocal
from backend.models.security import SecurityCheck, SecurityControl
from sqlalchemy import select

async def verify_seed():
    async with AsyncSessionLocal() as session:
        # Check Controls
        result = await session.execute(select(SecurityControl))
        controls = result.scalars().all()
        print(f"Total Controls: {len(controls)}")
        for c in controls:
            print(f" - {c.id}: {c.title}")

        # Check Checks
        result = await session.execute(select(SecurityCheck))
        checks = result.scalars().all()
        print(f"\nTotal Checks: {len(checks)}")
        for c in checks:
            print(f" - {c.id} (maps to {c.control_id}): {c.name}")

if __name__ == "__main__":
    asyncio.run(verify_seed())
