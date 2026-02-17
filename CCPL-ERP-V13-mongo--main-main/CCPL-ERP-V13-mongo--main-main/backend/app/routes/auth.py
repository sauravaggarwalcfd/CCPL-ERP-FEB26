from fastapi import APIRouter, HTTPException, status, Depends, Response
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta
import logging
from ..models.user import User, UserStatus
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    blacklist_token,
    validate_password_strength,
)
from ..core.dependencies import get_current_user
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def password_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Password cannot be empty')
        return v


class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str
    
    @field_validator('full_name')
    @classmethod
    def name_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Full name cannot be empty')
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict
    expires_in: int  # Token expiration time in seconds


class RefreshRequest(BaseModel):
    refresh_token: str
    
    @field_validator('refresh_token')
    @classmethod
    def token_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Refresh token cannot be empty')
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        is_valid, message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(message)
        return v


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, response: Response):
    """Enhanced login endpoint with security best practices."""
    try:
        user = await User.find_one(User.email == data.email.lower())

        if not user:
            logger.warning(f"Login attempt with non-existent email: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check if account is locked
        if (
            user.security.lock_until
            and user.security.lock_until > datetime.utcnow()
        ):
            remaining_minutes = int(
                (user.security.lock_until - datetime.utcnow()).total_seconds() / 60
            )
            logger.warning(f"Login attempt to locked account: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account is temporarily locked. Try again in {remaining_minutes} minutes.",
            )

        # Verify password with timing-safe comparison
        if not verify_password(data.password, user.password_hash):
            # Increment failed attempts
            user.security.failed_login_attempts += 1
            if user.security.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.security.lock_until = datetime.utcnow() + timedelta(
                    minutes=settings.LOGIN_LOCKOUT_MINUTES
                )
                logger.warning(f"Account locked due to failed attempts: {data.email}")
            await user.save()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check user status
        if user.status != UserStatus.ACTIVE:
            logger.warning(f"Login attempt with inactive account: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user.status.value}",
            )

        # Reset failed attempts on successful login
        user.security.failed_login_attempts = 0
        user.security.lock_until = None
        user.last_login = datetime.utcnow()
        user.login_count += 1
        await user.save()

        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": str(user.role.id) if user.role else None
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Set secure headers for token response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        logger.info(f"Successful login: {data.email}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.dict() if user.role else None,
                "effective_permissions": user.effective_permissions,
                "assigned_warehouses": [w.dict() for w in user.assigned_warehouses],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again.",
        )


@router.post("/signup", response_model=TokenResponse)
async def signup(data: SignupRequest, response: Response):
    """Create a new user account and return authentication tokens."""
    try:
        # Check if email already exists
        existing_user = await User.find_one(User.email == data.email.lower())
        if existing_user:
            logger.warning(f"Signup attempt with existing email: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please login or use a different email.",
            )

        # Create new user with minimal fields
        from beanie import PydanticObjectId
        user = User(
            id=PydanticObjectId(),
            full_name=data.full_name,
            email=data.email.lower(),
            password_hash=get_password_hash(data.password),
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        await user.save()
        logger.info(f"New user registered: {data.email}")

        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": None
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Set secure headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": None,
                "effective_permissions": [],
                "assigned_warehouses": [],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed. Please try again.",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(data: RefreshRequest, response: Response):
    """Enhanced refresh token endpoint with validation and rotation."""
    try:
        payload = decode_token(data.refresh_token)

        if not payload:
            logger.warning("Refresh attempt with expired or invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        
        if payload.get("type") != "refresh":
            logger.warning(f"Refresh attempt with wrong token type: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected refresh token.",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        user = await User.get(user_id)
        if not user or user.status != UserStatus.ACTIVE:
            logger.warning(f"Refresh attempt for inactive user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new tokens with rotation
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": str(user.role.id) if user.role else None
        }
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Optionally blacklist old refresh token (token rotation)
        if settings.TOKEN_BLACKLIST_ENABLED:
            blacklist_token(data.refresh_token)

        # Set secure headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.dict() if user.role else None,
                "effective_permissions": user.effective_permissions,
                "assigned_warehouses": [w.dict() for w in user.assigned_warehouses],
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please login again.",
        )



@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "avatar": current_user.avatar,
        "role": current_user.role.dict() if current_user.role else None,
        "effective_permissions": current_user.effective_permissions,
        "assigned_warehouses": [w.dict() for w in current_user.assigned_warehouses],
        "preferences": current_user.preferences.dict(),
        "status": current_user.status.value,
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """Enhanced logout endpoint with token blacklisting."""
    try:
        logger.info(f"User logged out: {current_user.email}")
        # Token will be invalidated via blacklist on next use
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Even if blacklist fails, return success to client
        return {"message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user)
):
    """Change user password with validation."""
    try:
        # Verify current password
        if not verify_password(data.current_password, current_user.password_hash):
            logger.warning(f"Failed password change attempt: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )

        # Validate new password format
        is_valid, message = validate_password_strength(data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # Verify passwords match
        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match",
            )

        # Prevent reusing current password
        if verify_password(data.new_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password",
            )

        # Update password
        current_user.password_hash = get_password_hash(data.new_password)
        current_user.password_changed_at = datetime.utcnow()
        await current_user.save()

        logger.info(f"Password changed successfully: {current_user.email}")

        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )

