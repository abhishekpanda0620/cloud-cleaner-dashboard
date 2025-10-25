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


@router.get("/roles/{role_name}")
async def get_role_details(role_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific IAM role
    
    Args:
        role_name: The IAM role name
        
    Returns:
        Dictionary containing detailed role information
    """
    try:
        iam_client = get_iam_client()
        
        # Get role details
        role_response = iam_client.get_role(RoleName=role_name)
        role = role_response.get('Role', {})
        
        # Get attached policies
        attached_policies = []
        try:
            policies_response = iam_client.list_attached_role_policies(RoleName=role_name)
            attached_policies = [
                {
                    "name": policy.get('PolicyName'),
                    "arn": policy.get('PolicyArn')
                }
                for policy in policies_response.get('AttachedPolicies', [])
            ]
        except:
            pass
        
        # Get inline policies
        inline_policies = []
        try:
            inline_response = iam_client.list_role_policies(RoleName=role_name)
            inline_policies = inline_response.get('PolicyNames', [])
        except:
            pass
        
        # Get role tags
        tags = {}
        try:
            tags_response = iam_client.list_role_tags(RoleName=role_name)
            tags = {tag.get('Key'): tag.get('Value') for tag in tags_response.get('Tags', [])}
        except:
            pass
        
        # Get last used information
        role_last_used = role.get('RoleLastUsed', {})
        
        details = {
            "name": role.get('RoleName'),
            "arn": role.get('Arn'),
            "role_id": role.get('RoleId'),
            "path": role.get('Path'),
            "create_date": role.get('CreateDate').isoformat() if role.get('CreateDate') else None,
            "description": role.get('Description', 'N/A'),
            "max_session_duration": role.get('MaxSessionDuration'),
            "last_used_date": role_last_used.get('LastUsedDate').isoformat() if role_last_used.get('LastUsedDate') else None,
            "last_used_region": role_last_used.get('Region'),
            "assume_role_policy": role.get('AssumeRolePolicyDocument'),
            "attached_policies": attached_policies,
            "inline_policies": inline_policies,
            "tags": tags
        }
        
        logger.info(f"Retrieved details for role {role_name}")
        return details
        
    except iam_client.exceptions.NoSuchEntityException:
        raise HTTPException(status_code=404, detail=f"Role {role_name} not found")
    except Exception as e:
        logger.error(f"Error fetching role details for {role_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch role details: {str(e)}"
        )


@router.delete("/roles/{role_name}")
async def delete_role(role_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Delete an IAM role
    
    Args:
        role_name: The IAM role name to delete
        force: If True, detach all policies and delete the role
        
    Returns:
        Dictionary containing deletion status
    """
    try:
        iam_client = get_iam_client()
        
        # Check if role exists
        try:
            iam_client.get_role(RoleName=role_name)
        except iam_client.exceptions.NoSuchEntityException:
            raise HTTPException(status_code=404, detail=f"Role {role_name} not found")
        
        if force:
            # Detach all managed policies
            try:
                policies_response = iam_client.list_attached_role_policies(RoleName=role_name)
                for policy in policies_response.get('AttachedPolicies', []):
                    iam_client.detach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy.get('PolicyArn')
                    )
                    logger.info(f"Detached policy {policy.get('PolicyName')} from role {role_name}")
            except:
                pass
            
            # Delete all inline policies
            try:
                inline_response = iam_client.list_role_policies(RoleName=role_name)
                for policy_name in inline_response.get('PolicyNames', []):
                    iam_client.delete_role_policy(
                        RoleName=role_name,
                        PolicyName=policy_name
                    )
                    logger.info(f"Deleted inline policy {policy_name} from role {role_name}")
            except:
                pass
            
            # Remove role from instance profiles
            try:
                profiles_response = iam_client.list_instance_profiles_for_role(RoleName=role_name)
                for profile in profiles_response.get('InstanceProfiles', []):
                    iam_client.remove_role_from_instance_profile(
                        InstanceProfileName=profile.get('InstanceProfileName'),
                        RoleName=role_name
                    )
                    logger.info(f"Removed role {role_name} from instance profile {profile.get('InstanceProfileName')}")
            except:
                pass
        
        # Delete the role
        iam_client.delete_role(RoleName=role_name)
        
        logger.info(f"Deleted role {role_name}")
        
        return {
            "success": True,
            "role_name": role_name,
            "message": f"Role {role_name} has been deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role {role_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete role: {str(e)}"
        )


@router.get("/users/{user_name}")
async def get_user_details(user_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific IAM user
    
    Args:
        user_name: The IAM user name
        
    Returns:
        Dictionary containing detailed user information
    """
    try:
        iam_client = get_iam_client()
        
        # Get user details
        user_response = iam_client.get_user(UserName=user_name)
        user = user_response.get('User', {})
        
        # Get attached policies
        attached_policies = []
        try:
            policies_response = iam_client.list_attached_user_policies(UserName=user_name)
            attached_policies = [
                {
                    "name": policy.get('PolicyName'),
                    "arn": policy.get('PolicyArn')
                }
                for policy in policies_response.get('AttachedPolicies', [])
            ]
        except:
            pass
        
        # Get inline policies
        inline_policies = []
        try:
            inline_response = iam_client.list_user_policies(UserName=user_name)
            inline_policies = inline_response.get('PolicyNames', [])
        except:
            pass
        
        # Get access keys
        access_keys = []
        try:
            keys_response = iam_client.list_access_keys(UserName=user_name)
            access_keys = [
                {
                    "access_key_id": key.get('AccessKeyId'),
                    "status": key.get('Status'),
                    "create_date": key.get('CreateDate').isoformat() if key.get('CreateDate') else None
                }
                for key in keys_response.get('AccessKeyMetadata', [])
            ]
        except:
            pass
        
        # Check console access
        has_console_access = False
        try:
            iam_client.get_login_profile(UserName=user_name)
            has_console_access = True
        except:
            pass
        
        # Get user groups
        groups = []
        try:
            groups_response = iam_client.list_groups_for_user(UserName=user_name)
            groups = [group.get('GroupName') for group in groups_response.get('Groups', [])]
        except:
            pass
        
        # Get user tags
        tags = {}
        try:
            tags_response = iam_client.list_user_tags(UserName=user_name)
            tags = {tag.get('Key'): tag.get('Value') for tag in tags_response.get('Tags', [])}
        except:
            pass
        
        details = {
            "name": user.get('UserName'),
            "arn": user.get('Arn'),
            "user_id": user.get('UserId'),
            "path": user.get('Path'),
            "create_date": user.get('CreateDate').isoformat() if user.get('CreateDate') else None,
            "password_last_used": user.get('PasswordLastUsed').isoformat() if user.get('PasswordLastUsed') else None,
            "has_console_access": has_console_access,
            "attached_policies": attached_policies,
            "inline_policies": inline_policies,
            "access_keys": access_keys,
            "groups": groups,
            "tags": tags
        }
        
        logger.info(f"Retrieved details for user {user_name}")
        return details
        
    except iam_client.exceptions.NoSuchEntityException:
        raise HTTPException(status_code=404, detail=f"User {user_name} not found")
    except Exception as e:
        logger.error(f"Error fetching user details for {user_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user details: {str(e)}"
        )


@router.delete("/users/{user_name}")
async def delete_user(user_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Delete an IAM user
    
    Args:
        user_name: The IAM user name to delete
        force: If True, remove all user resources before deletion
        
    Returns:
        Dictionary containing deletion status
    """
    try:
        iam_client = get_iam_client()
        
        # Check if user exists
        try:
            iam_client.get_user(UserName=user_name)
        except iam_client.exceptions.NoSuchEntityException:
            raise HTTPException(status_code=404, detail=f"User {user_name} not found")
        
        if force:
            # Delete login profile
            try:
                iam_client.delete_login_profile(UserName=user_name)
                logger.info(f"Deleted login profile for user {user_name}")
            except:
                pass
            
            # Delete access keys
            try:
                keys_response = iam_client.list_access_keys(UserName=user_name)
                for key in keys_response.get('AccessKeyMetadata', []):
                    iam_client.delete_access_key(
                        UserName=user_name,
                        AccessKeyId=key.get('AccessKeyId')
                    )
                    logger.info(f"Deleted access key {key.get('AccessKeyId')} for user {user_name}")
            except:
                pass
            
            # Detach managed policies
            try:
                policies_response = iam_client.list_attached_user_policies(UserName=user_name)
                for policy in policies_response.get('AttachedPolicies', []):
                    iam_client.detach_user_policy(
                        UserName=user_name,
                        PolicyArn=policy.get('PolicyArn')
                    )
                    logger.info(f"Detached policy {policy.get('PolicyName')} from user {user_name}")
            except:
                pass
            
            # Delete inline policies
            try:
                inline_response = iam_client.list_user_policies(UserName=user_name)
                for policy_name in inline_response.get('PolicyNames', []):
                    iam_client.delete_user_policy(
                        UserName=user_name,
                        PolicyName=policy_name
                    )
                    logger.info(f"Deleted inline policy {policy_name} from user {user_name}")
            except:
                pass
            
            # Remove from groups
            try:
                groups_response = iam_client.list_groups_for_user(UserName=user_name)
                for group in groups_response.get('Groups', []):
                    iam_client.remove_user_from_group(
                        UserName=user_name,
                        GroupName=group.get('GroupName')
                    )
                    logger.info(f"Removed user {user_name} from group {group.get('GroupName')}")
            except:
                pass
        
        # Delete the user
        iam_client.delete_user(UserName=user_name)
        
        logger.info(f"Deleted user {user_name}")
        
        return {
            "success": True,
            "user_name": user_name,
            "message": f"User {user_name} has been deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {str(e)}"
        )
