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


@router.get("/users/unused")
async def get_unused_iam_users() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of IAM users with no console or programmatic access in 90+ days
    
    Returns:
        Dictionary containing list of potentially unused IAM users
    """
    try:
        iam_client = get_iam_client()
        
        # Get all users
        paginator = iam_client.get_paginator('list_users')
        
        unused_users = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        for page in paginator.paginate():
            for user in page.get('Users', []):
                user_name = user.get('UserName')
                create_date = user.get('CreateDate')
                
                try:
                    # Get user access key information
                    access_keys = iam_client.list_access_keys(UserName=user_name)
                    keys = access_keys.get('AccessKeyMetadata', [])
                    
                    # Get login profile (console access)
                    has_console_access = False
                    try:
                        iam_client.get_login_profile(UserName=user_name)
                        has_console_access = True
                    except:
                        has_console_access = False
                    
                    # Check if user has any recent activity
                    last_console_login = None
                    last_key_access = None
                    
                    try:
                        user_details = iam_client.get_user(UserName=user_name)
                        # Note: LastUsed info is not directly available in get_user
                        # This would require CloudTrail analysis for production use
                    except:
                        pass
                    
                    # Consider user unused if no access keys and no console access
                    # or if they have access but haven't used it recently
                    is_unused = False
                    if not has_console_access and len(keys) == 0:
                        is_unused = True
                    
                    if is_unused or (has_console_access or len(keys) > 0):
                        unused_users.append({
                            "name": user_name,
                            "create_date": create_date.isoformat() if create_date else None,
                            "arn": user.get('Arn'),
                            "has_console_access": has_console_access,
                            "access_keys_count": len(keys),
                            "access_keys": [
                                {
                                    "access_key_id": key.get('AccessKeyId'),
                                    "status": key.get('Status'),
                                    "create_date": key.get('CreateDate').isoformat() if key.get('CreateDate') else None
                                }
                                for key in keys
                            ]
                        })
                        
                except Exception as e:
                    logger.warning(f"Could not check user {user_name}: {str(e)}")
                    continue
        
        logger.info(f"Found {len(unused_users)} IAM users")
        return {"unused_users": unused_users}
        
    except Exception as e:
        logger.error(f"Error fetching IAM users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch IAM users: {str(e)}"
        )


@router.get("/access-keys/unused")
async def get_unused_access_keys() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get list of access keys that haven't been used in 90+ days
    
    Returns:
        Dictionary containing list of potentially unused access keys
    """
    try:
        iam_client = get_iam_client()
        
        # Get all users
        paginator = iam_client.get_paginator('list_users')
        
        unused_keys = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        for page in paginator.paginate():
            for user in page.get('Users', []):
                user_name = user.get('UserName')
                
                try:
                    # Get access keys for user
                    access_keys = iam_client.list_access_keys(UserName=user_name)
                    keys = access_keys.get('AccessKeyMetadata', [])
                    
                    for key in keys:
                        key_id = key.get('AccessKeyId')
                        create_date = key.get('CreateDate')
                        status = key.get('Status')
                        
                        # Get last used information
                        try:
                            key_last_used = iam_client.get_access_key_last_used(AccessKeyId=key_id)
                            last_used_info = key_last_used.get('AccessKeyLastUsed', {})
                            last_used_date = last_used_info.get('LastUsedDate')
                        except:
                            last_used_date = None
                        
                        # Consider key unused if never used or not used in 90+ days
                        is_unused = False
                        if last_used_date is None:
                            is_unused = True
                        elif last_used_date < cutoff_date:
                            is_unused = True
                        
                        if is_unused:
                            unused_keys.append({
                                "access_key_id": key_id,
                                "user_name": user_name,
                                "status": status,
                                "create_date": create_date.isoformat() if create_date else None,
                                "last_used_date": last_used_date.isoformat() if last_used_date else None,
                                "security_risk": "High" if status == "Active" else "Low"
                            })
                        
                except Exception as e:
                    logger.warning(f"Could not check access keys for user {user_name}: {str(e)}")
                    continue
        
        logger.info(f"Found {len(unused_keys)} potentially unused access keys")
        return {"unused_keys": unused_keys}
        
    except Exception as e:
        logger.error(f"Error fetching unused access keys: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch access keys: {str(e)}"
        )
