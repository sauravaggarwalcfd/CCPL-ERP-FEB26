from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class AuditAction(str, Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    EXPORT = "EXPORT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class AuditUser(BaseModel):
    id: str
    email: str
    name: str
    role: Optional[str] = None


class AuditResource(BaseModel):
    type: str  # Product, Order, User
    id: str
    identifier: Optional[str] = None  # SKU, Order Number


class AuditChanges(BaseModel):
    before: Optional[Any] = None
    after: Optional[Any] = None
    fields: List[str] = []


class AuditContext(BaseModel):
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None


class AuditLog(SheetDocument):
    user: AuditUser
    action: AuditAction
    module: str
    resource: Optional[AuditResource] = None
    changes: Optional[AuditChanges] = None
    context: Optional[AuditContext] = None
    status: str = "success"  # success, failure
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "audit_logs"
        unique_fields = []
