from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from core.aws_client import get_iam_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/unused")
async def get_unused_iam_roles() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of IAM roles that haven't been used in 90+ days
    
    Returns:
        Dictionary containing list of potentially unused IAM roles
    """
    try:
        iam_client = get_iam_client()
        
        # Get all roles
        paginator = iam_client.get_paginator('list_roles')
        
        unused_roles = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        for page in paginator.paginate():
            for role in page.get('Roles', []):
                role_name = role.get('RoleName')
                create_date = role.get('CreateDate')
                
                try:
                    # Get role last used information
                    role_details = iam_client.get_role(RoleName=role_name)
                    role_last_used = role_details.get('Role', {}).get('RoleLastUsed', {})
                    last_used_date = role_last_used.get('LastUsedDate')
                    
                    # Consider role unused if never used or not used in 90+ days
                    is_unused = False
                    if last_used_date is None:
                        is_unused = True
                    elif last_used_date < cutoff_date:
                        is_unused = True
                    
                    if is_unused:
                        unused_roles.append({
                            "name": role_name,
                            "create_date": create_date.isoformat() if create_date else None,
                            "last_used_date": last_used_date.isoformat() if last_used_date else None,
                            "arn": role.get('Arn'),
                            "description": role.get('Description', 'N/A')
                        })
                        
                except Exception as e:
                    logger.warning(f"Could not check role {role_name}: {str(e)}")
                    continue
        
        logger.info(f"Found {len(unused_roles)} potentially unused IAM roles")
        return {"unused_roles": unused_roles}
        
    except Exception as e:
        logger.error(f"Error fetching unused IAM roles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch IAM roles: {str(e)}"
        )


@router.get("/all")
async def get_all_roles() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of all IAM roles
    
    Returns:
        Dictionary containing list of all IAM roles
    """
    try:
        iam_client = get_iam_client()
        
        # Get all roles
        paginator = iam_client.get_paginator('list_roles')
        
        roles = []
        for page in paginator.paginate():
            for role in page.get('Roles', []):
                role_name = role.get('RoleName')
                create_date = role.get('CreateDate')
                
                try:
                    # Get role last used information
                    role_details = iam_client.get_role(RoleName=role_name)
                    role_last_used = role_details.get('Role', {}).get('RoleLastUsed', {})
                    last_used_date = role_last_used.get('LastUsedDate')
                    
                    roles.append({
                        "name": role_name,
                        "create_date": create_date.isoformat() if create_date else None,
                        "last_used_date": last_used_date.isoformat() if last_used_date else None,
                        "arn": role.get('Arn'),
                        "description": role.get('Description', 'N/A')
                    })
                except Exception as e:
                    logger.warning(f"Could not get details for role {role_name}: {str(e)}")
                    roles.append({
                        "name": role_name,
                        "create_date": create_date.isoformat() if create_date else None,
                        "last_used_date": None,
                        "arn": role.get('Arn'),
                        "description": role.get('Description', 'N/A')
                    })
        
        logger.info(f"Found {len(roles)} total IAM roles")
        return {"roles": roles}
        
    except Exception as e:
        logger.error(f"Error fetching all IAM roles: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch IAM roles: {str(e)}"
        )
