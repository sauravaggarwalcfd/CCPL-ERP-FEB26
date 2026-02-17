from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging
from .security import decode_token
from ..models.user import User

security = HTTPBearer()
logger = logging.getLogger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Extract and validate current user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        logger.warning("Invalid or expired token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        logger.warning(f"Invalid token type: {payload.get('type')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        logger.warning("Token missing user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.get(user_id)
    if user is None:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != "active":
        logger.warning(f"Inactive user attempted access: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure current user is active."""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


# Permission checker dependency factory
def require_permissions(required_permissions: List[str]):
    """Factory to create permission checker dependencies."""
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        # Super admin bypasses all checks
        if current_user.role and current_user.role.slug == "super-admin":
            return current_user

        has_permission = current_user.has_any_permission(required_permissions)

        if not has_permission:
            logger.warning(
                f"User {current_user.email} attempted access without required permissions: {required_permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_permissions}",
            )

        return current_user
    
    return permission_checker


    return permission_checker


# Warehouse access checker
def require_warehouse_access(warehouse_id: str):
    async def warehouse_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.can_access_warehouse(warehouse_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this warehouse",
            )
        return current_user

    return warehouse_checker
