from .sheet_document import SheetDocument
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class WarehouseAccess(str, Enum):
    ALL = "all"
    ASSIGNED = "assigned"
    NONE = "none"


class DataScope(str, Enum):
    ALL = "all"
    TEAM = "team"
    OWN = "own"


# Embedded Models
class EmbeddedRole(BaseModel):
    id: Optional[str] = None
    name: str
    slug: str
    level: int = 30


class EmbeddedWarehouse(BaseModel):
    id: str
    code: str
    name: str
    is_primary: bool = False


class EmbeddedUser(BaseModel):
    id: str
    name: str
    email: Optional[str] = None


class UserSession(BaseModel):
    token: str
    device: Optional[str] = None
    browser: Optional[str] = None
    ip: Optional[str] = None
    last_active: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class SecuritySettings(BaseModel):
    password_changed_at: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    failed_login_attempts: int = 0
    lock_until: Optional[datetime] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    must_change_password: bool = False


class UserPreferences(BaseModel):
    language: str = "en"
    timezone: str = "Asia/Kolkata"
    date_format: str = "DD/MM/YYYY"
    theme: str = "light"  # light, dark, system
    default_warehouse_id: Optional[str] = None
    notifications: dict = {
        "email": True,
        "in_app": True,
        "low_stock": True,
        "orders": True,
    }


class InvitationInfo(BaseModel):
    token: Optional[str] = None
    invited_by: Optional[EmbeddedUser] = None
    invited_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None


# Main User Document
class User(SheetDocument):
    email: str  # EmailStr removed for sheet compat
    password_hash: str
    full_name: str
    phone: Optional[str] = None
    avatar: Optional[str] = None

    # Role & Permissions
    role: Optional[EmbeddedRole] = None
    additional_permissions: List[str] = []
    denied_permissions: List[str] = []
    effective_permissions: List[str] = []

    # Team
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    manager: Optional[EmbeddedUser] = None

    # Warehouse Access
    assigned_warehouses: List[EmbeddedWarehouse] = []

    # Status
    status: UserStatus = UserStatus.PENDING

    # Security
    security: SecuritySettings = SecuritySettings()

    # Sessions
    sessions: List[UserSession] = []

    # Invitation
    invitation: Optional[InvitationInfo] = None

    # Preferences
    preferences: UserPreferences = UserPreferences()

    # Activity
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None
    login_count: int = 0

    # Metadata
    created_by: Optional[EmbeddedUser] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_users"
        unique_fields = ["email"]

    def has_permission(self, permission_code: str) -> bool:
        if permission_code in self.denied_permissions:
            return False
        return (
            permission_code in self.effective_permissions
            or permission_code in self.additional_permissions
        )

    def has_any_permission(self, permission_codes: List[str]) -> bool:
        return any(self.has_permission(p) for p in permission_codes)

    def has_all_permissions(self, permission_codes: List[str]) -> bool:
        return all(self.has_permission(p) for p in permission_codes)

    def can_access_warehouse(self, warehouse_id: str) -> bool:
        if self.role and self.role.slug == "super-admin":
            return True
        return any(w.id == warehouse_id for w in self.assigned_warehouses)
