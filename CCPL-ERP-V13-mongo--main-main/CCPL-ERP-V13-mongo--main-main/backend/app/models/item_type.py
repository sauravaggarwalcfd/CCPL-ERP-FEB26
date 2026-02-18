"""
Item Type Master Model
Defines types of items: Raw Material, Finished Goods, etc.

Table: item_types
Code Format: 2 characters (e.g., FG, RM, AC, CM, SG)
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DefaultUOM(str, Enum):
    PCS = "PCS"
    KG = "KG"
    MTR = "MTR"
    LTR = "LTR"
    DOZ = "DOZ"
    SET = "SET"
    ROLL = "ROLL"
    BOX = "BOX"


class ItemType(SheetDocument):
    """Item Type Master - 10 types for apparel manufacturing"""

    type_code: str
    type_name: str
    description: Optional[str] = None

    allow_purchase: bool = True
    allow_sale: bool = False
    track_inventory: bool = True
    require_quality_check: bool = False

    default_uom: str = "PCS"
    color_code: str = "#6b7280"
    icon: str = "Package"
    sort_order: int = 0

    is_active: bool = True
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "item_types"
        unique_fields = ["type_code"]


class ItemTypeCreate(BaseModel):
    type_code: str = Field(..., min_length=2, max_length=20)
    type_name: str
    description: Optional[str] = None
    allow_purchase: bool = True
    allow_sale: bool = False
    track_inventory: bool = True
    require_quality_check: bool = False
    default_uom: str = "PCS"
    color_code: str = "#6b7280"
    icon: str = "Package"
    sort_order: int = 0
    
    @field_validator('type_code')
    @classmethod
    def validate_code(cls, v):
        if not v.isalnum():
            raise ValueError('Code must be alphanumeric')
        return v.upper()


class ItemTypeUpdate(BaseModel):
    type_name: Optional[str] = None
    description: Optional[str] = None
    allow_purchase: Optional[bool] = None
    allow_sale: Optional[bool] = None
    track_inventory: Optional[bool] = None
    require_quality_check: Optional[bool] = None
    default_uom: Optional[str] = None
    color_code: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ItemTypeResponse(BaseModel):
    id: str
    type_code: str
    type_name: str
    description: Optional[str]
    allow_purchase: bool
    allow_sale: bool
    track_inventory: bool
    require_quality_check: bool
    default_uom: str
    color_code: str
    icon: str
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


SEED_ITEM_TYPES = [
    {"type_code": "YN", "type_name": "Yarn & Fiber", "description": "Yarns and fibers for manufacturing", "allow_purchase": True, "allow_sale": False, "default_uom": "KG", "color_code": "#8b5cf6", "icon": "Circle", "sort_order": 1},
    {"type_code": "GF", "type_name": "Grey Fabric", "description": "Unprocessed grey fabric", "allow_purchase": True, "allow_sale": False, "default_uom": "MTR", "color_code": "#6b7280", "icon": "Layers", "sort_order": 2},
    {"type_code": "DF", "type_name": "Dyed Fabric", "description": "Processed and dyed fabric", "allow_purchase": True, "allow_sale": False, "default_uom": "MTR", "color_code": "#3b82f6", "icon": "Layers", "sort_order": 3},
    {"type_code": "TR", "type_name": "Trims & Accessories", "description": "Buttons, zippers, labels, accessories", "allow_purchase": True, "allow_sale": False, "default_uom": "PCS", "color_code": "#f59e0b", "icon": "Sparkles", "sort_order": 4},
    {"type_code": "DY", "type_name": "Dyes & Chemicals", "description": "Dyes, chemicals for processing", "allow_purchase": True, "allow_sale": False, "default_uom": "LTR", "color_code": "#ef4444", "icon": "FlaskConical", "sort_order": 5},
    {"type_code": "CP", "type_name": "Cut Components", "description": "Cut fabric components", "allow_purchase": False, "allow_sale": False, "default_uom": "PCS", "color_code": "#ec4899", "icon": "Scissors", "sort_order": 6},
    {"type_code": "SF", "type_name": "Semi-Finished Goods", "description": "Semi-finished products/WIP", "allow_purchase": False, "allow_sale": False, "default_uom": "PCS", "color_code": "#f97316", "icon": "Loader", "sort_order": 7},
    {"type_code": "FG", "type_name": "Finished Goods", "description": "Ready to sell products", "allow_purchase": False, "allow_sale": True, "require_quality_check": True, "default_uom": "PCS", "color_code": "#10b981", "icon": "Package", "sort_order": 8},
    {"type_code": "PK", "type_name": "Packaging Materials", "description": "Polybags, cartons, tags", "allow_purchase": True, "allow_sale": False, "default_uom": "PCS", "color_code": "#06b6d4", "icon": "Box", "sort_order": 9},
    {"type_code": "CS", "type_name": "Consumables & Spares", "description": "Needles, oil, tools, spares", "allow_purchase": True, "allow_sale": False, "default_uom": "PCS", "color_code": "#64748b", "icon": "Wrench", "sort_order": 10},
]
