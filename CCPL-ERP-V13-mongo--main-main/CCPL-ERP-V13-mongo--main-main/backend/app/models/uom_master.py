"""
UOM (Unit of Measure) Master Model
Manages UOM variants with grouping and conversion system
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UOMGroup(str, Enum):
    """Pre-defined UOM groups"""
    WEIGHT = "WEIGHT"
    LENGTH = "LENGTH"
    VOLUME = "VOLUME"
    COUNT = "COUNT"
    AREA = "AREA"


class UOMMaster(Document):
    """UOM Master Document"""
    uom_code: Indexed(str, unique=True)
    uom_name: str
    uom_group: str  # Changed from Enum to str
    group_name: str  # Display name
    uom_symbol: str  # Symbol for display (kg, m, l, pcs, etc.)
    conversion_to_base: float = 1.0  # Conversion factor to base unit
    is_base_uom: bool = False  # Is this the base unit in the group?
    is_active: bool = True
    display_order: int = 0
    description: Optional[str] = None

    # Audit fields
    created_by: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified_by: Optional[str] = None
    last_modified_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "uom_master"
        indexes = [
            "uom_code",
            "uom_group",
            "is_active",
            "display_order",
            "is_base_uom"
        ]


# ==================== REQUEST SCHEMAS ====================

class UOMCreate(BaseModel):
    uom_code: str = Field(..., min_length=1, max_length=20)
    uom_name: str
    uom_group: str
    uom_symbol: str
    conversion_to_base: float = 1.0
    is_base_uom: bool = False
    description: Optional[str] = None
    display_order: int = 0

    @field_validator('uom_code')
    @classmethod
    def validate_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Code must be alphanumeric (with - or _ allowed)')
        return v.upper()


class UOMUpdate(BaseModel):
    uom_name: Optional[str] = None
    uom_group: Optional[str] = None
    uom_symbol: Optional[str] = None
    conversion_to_base: Optional[float] = None
    is_base_uom: Optional[bool] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class UOMResponse(BaseModel):
    id: str
    uom_code: str
    uom_name: str
    uom_group: str
    group_name: str
    uom_symbol: str
    conversion_to_base: float
    is_base_uom: bool
    is_active: bool
    display_order: int
    description: Optional[str]
    created_by: Optional[str]
    created_date: datetime
    last_modified_by: Optional[str]
    last_modified_date: datetime


# ==================== GROUP DISPLAY NAMES ====================

UOM_GROUP_NAMES = {
    UOMGroup.WEIGHT: "Weight Units",
    UOMGroup.LENGTH: "Length Units",
    UOMGroup.VOLUME: "Volume Units",
    UOMGroup.COUNT: "Count Units",
    UOMGroup.AREA: "Area Units"
}


# ==================== CONVERSION HELPER ====================

def convert_uom(value: float, from_uom: UOMMaster, to_uom: UOMMaster) -> float:
    """
    Convert value from one UOM to another within the same group

    Args:
        value: The value to convert
        from_uom: Source UOM
        to_uom: Target UOM

    Returns:
        Converted value

    Raises:
        ValueError: If UOMs are not in the same group
    """
    if from_uom.uom_group != to_uom.uom_group:
        raise ValueError(f"Cannot convert between different UOM groups: {from_uom.uom_group} and {to_uom.uom_group}")

    # Convert to base unit first, then to target unit
    base_value = value * from_uom.conversion_to_base
    target_value = base_value / to_uom.conversion_to_base

    return target_value
