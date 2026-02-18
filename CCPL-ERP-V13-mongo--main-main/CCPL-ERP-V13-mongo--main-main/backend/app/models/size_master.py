"""
Size Master Model
Manages size variants with grouping system
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class SizeGroup(str, Enum):
    """Pre-defined size groups"""
    APPAREL_SIZES = "APPAREL_SIZES"
    STANDARD_SIZES = "STANDARD_SIZES"
    NUMERIC_SIZES = "NUMERIC_SIZES"
    CUSTOM_SIZES = "CUSTOM_SIZES"


class SizeMaster(SheetDocument):
    """Size Master Document"""
    size_code: str
    size_name: str
    size_group: str  # Changed from Enum to str
    group_name: str  # Display name
    numeric_value: Optional[float] = None  # For numeric sizes (32, 34, 36, etc.)
    unit: str = "SIZE"  # Unit label
    is_active: bool = True
    display_order: int = 0
    description: Optional[str] = None

    # Audit fields
    created_by: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified_by: Optional[str] = None
    last_modified_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_size_master"
        unique_fields = ["size_code"]


# ==================== REQUEST SCHEMAS ====================

class SizeCreate(BaseModel):
    size_code: str = Field(..., min_length=1, max_length=20)
    size_name: str
    size_group: str
    numeric_value: Optional[float] = None
    unit: str = "SIZE"
    description: Optional[str] = None
    display_order: int = 0

    @field_validator('size_code')
    @classmethod
    def validate_code(cls, v):
        if not v.replace('-', '').replace('_', '').replace('.', '').isalnum():
            raise ValueError('Code must be alphanumeric (with -, _, . allowed)')
        return v.upper()


class SizeUpdate(BaseModel):
    size_name: Optional[str] = None
    size_group: Optional[str] = None
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class SizeResponse(BaseModel):
    id: str
    size_code: str
    size_name: str
    size_group: str
    group_name: str
    numeric_value: Optional[float]
    unit: str
    is_active: bool
    display_order: int
    description: Optional[str]
    created_by: Optional[str]
    created_date: datetime
    last_modified_by: Optional[str]
    last_modified_date: datetime


# ==================== GROUP DISPLAY NAMES ====================

SIZE_GROUP_NAMES = {
    SizeGroup.APPAREL_SIZES: "Apparel Sizes",
    SizeGroup.STANDARD_SIZES: "Standard Sizes",
    SizeGroup.NUMERIC_SIZES: "Numeric Sizes",
    SizeGroup.CUSTOM_SIZES: "Custom Sizes"
}
