from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any

from models import get_db
from models.security import SecurityFinding, SecurityCheck, SecurityControl
from services.aws.security_service import SecurityService

router = APIRouter(prefix="/security", tags=["security"])

@router.post("/scan")
async def trigger_security_scan(
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger an on-demand security scan.
    Note: In production this should be a Celery task.
    """
    service = SecurityService(db)
    try:
        findings = await service.run_all_scanners()
        return {"status": "success", "findings_count": len(findings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/findings")
async def get_findings(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all security findings with check details.
    """
    # We join with SecurityCheck to get the check name/severity
    stmt = select(SecurityFinding, SecurityCheck).join(SecurityCheck, SecurityFinding.check_id == SecurityCheck.id)
    result = await db.execute(stmt)
    
    output = []
    for finding, check in result:
        output.append({
            "id": finding.id,
            "check_id": finding.check_id,
            "check_name": check.name,
            "severity": check.severity,
            "status": finding.status,
            "resource_id": finding.resource_id,
            "region": finding.region,
            "evidence": finding.evidence,
            "last_updated": finding.last_updated_at
        })
    return output

@router.get("/controls")
async def get_controls(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all controls and their current status (rollup).
    """
    stmt = select(SecurityControl).order_by(SecurityControl.control_code)
    result = await db.execute(stmt)
    controls = result.scalars().all()
    return controls

@router.get("/stats")
async def get_security_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get compliance statistics.
    """
    pass_count = await db.scalar(
        select(func.count()).where(SecurityFinding.status == 'PASS')
    )
    fail_count = await db.scalar(
        select(func.count()).where(SecurityFinding.status == 'FAIL')
    )
    
    return {
        "pass": pass_count or 0,
        "fail": fail_count or 0,
        "total": (pass_count or 0) + (fail_count or 0),
        "score": round((pass_count / ((pass_count + fail_count) or 1)) * 100)
    }
