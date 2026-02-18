"""
Variant Groups Model
Master definitions for variant group categories
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class VariantType(str, Enum):
    """Types of variants"""
    COLOUR = "COLOUR"
    SIZE = "SIZE"
    UOM = "UOM"


class VariantGroup(SheetDocument):
    """Variant Group Definitions"""
    variant_type: str  # COLOUR, SIZE, UOM
    group_code: str  # THREAD_COLORS, APPAREL_SIZES, WEIGHT, etc.
    group_name: str  # Display name
    description: Optional[str] = None
    is_active: bool = True
    display_order: int = 0
    created_date: datetime = datetime.utcnow()

    class Settings:
        name = "_variant_groups"
        unique_fields = ["variant_type", "group_code"]


# ==================== RESPONSE SCHEMA ====================

class VariantGroupResponse(BaseModel):
    id: str
    variant_type: str
    group_code: str
    group_name: str
    description: Optional[str]
    is_active: bool
    display_order: int
    created_date: datetime

# ==================== CREATE/UPDATE SCHEMAS ====================

class VariantGroupCreate(BaseModel):
    variant_type: VariantType
    group_code: str
    group_name: str
    description: Optional[str] = None
    is_active: bool = True
    display_order: int = 0

class VariantGroupUpdate(BaseModel):
    group_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


# ==================== SEED DATA ====================

VARIANT_GROUPS_SEED = [
    # Colour Groups
    {"variant_type": "COLOUR", "group_code": "THREAD_COLORS", "group_name": "Thread Colors", "description": "Colors for threads and embroidery", "display_order": 1},
    {"variant_type": "COLOUR", "group_code": "FABRIC_COLORS", "group_name": "Fabric Colors", "description": "Colors for fabrics and materials", "display_order": 2},
    {"variant_type": "COLOUR", "group_code": "BUTTON_COLORS", "group_name": "Button Colors", "description": "Colors for buttons and fasteners", "display_order": 3},
    {"variant_type": "COLOUR", "group_code": "LABEL_COLORS", "group_name": "Label Colors", "description": "Colors for labels and tags", "display_order": 4},
    {"variant_type": "COLOUR", "group_code": "OTHER", "group_name": "Other Colors", "description": "Miscellaneous colors", "display_order": 5},

    # Size Groups
    {"variant_type": "SIZE", "group_code": "APPAREL_SIZES", "group_name": "Apparel Sizes", "description": "Standard apparel sizes (XS, S, M, L, XL)", "display_order": 1},
    {"variant_type": "SIZE", "group_code": "STANDARD_SIZES", "group_name": "Standard Sizes", "description": "Standard generic sizes (Small, Medium, Large)", "display_order": 2},
    {"variant_type": "SIZE", "group_code": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "description": "Numeric sizing (28, 30, 32, 34, etc.)", "display_order": 3},
    {"variant_type": "SIZE", "group_code": "CUSTOM_SIZES", "group_name": "Custom Sizes", "description": "Custom or special sizes", "display_order": 4},

    # UOM Groups
    {"variant_type": "UOM", "group_code": "WEIGHT", "group_name": "Weight Units", "description": "Units for measuring weight", "display_order": 1},
    {"variant_type": "UOM", "group_code": "LENGTH", "group_name": "Length Units", "description": "Units for measuring length/distance", "display_order": 2},
    {"variant_type": "UOM", "group_code": "VOLUME", "group_name": "Volume Units", "description": "Units for measuring volume/capacity", "display_order": 3},
    {"variant_type": "UOM", "group_code": "COUNT", "group_name": "Count Units", "description": "Units for counting items", "display_order": 4},
    {"variant_type": "UOM", "group_code": "AREA", "group_name": "Area Units", "description": "Units for measuring area", "display_order": 5},
]
