from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Permission(SheetDocument):
    code: str  # e.g., 'products.create'
    module: str  # products, inventory, sales, etc.
    action: str  # view, create, edit, delete, approve, export
    name: str  # Display name
    description: Optional[str] = None
    category: str = "core"  # core, operations, finance, admin
    is_system: bool = False
    is_active: bool = True

    class Settings:
        name = "permissions"
        unique_fields = ["code"]


class EmbeddedParentRole(BaseModel):
    id: str
    name: str
    slug: str


class DashboardConfig(BaseModel):
    widgets: List[str] = []
    default_page: str = "/dashboard"


class Role(SheetDocument):
    name: str
    slug: str
    description: Optional[str] = None

    # Permissions
    permission_ids: List[str] = []
    permission_codes: List[str] = []  # Denormalized for quick access

    # Hierarchy
    parent_role: Optional[EmbeddedParentRole] = None
    level: int = 30  # 100=SuperAdmin, 90=Admin, 70=Manager, 50=Staff, 30=Viewer

    # Access Control
    warehouse_access: str = "all"  # all, assigned, none
    data_scope: str = "all"  # all, team, own

    # UI Config
    dashboard: DashboardConfig = DashboardConfig()

    # Metadata
    is_system: bool = False
    is_active: bool = True
    created_by: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "roles"
        unique_fields = ["name", "slug"]

    def has_permission(self, permission_code: str) -> bool:
        return permission_code in self.permission_codes
