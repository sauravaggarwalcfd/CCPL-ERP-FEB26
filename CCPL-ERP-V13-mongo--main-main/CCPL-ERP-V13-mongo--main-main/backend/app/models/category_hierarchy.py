"""
5-Level Item Category Hierarchy Models
All codes are 2-4 characters (flexible length)

Level 1: Category (APRL, FABR, ACCS)
Level 2: Sub-Category (MENS, WMNS, KIDS)
Level 3: Division (TOPW, BTMW, ETHN)
Level 4: Class (TSHT, SHRT, JEAN)
Level 5: Sub-Class (RNCK, VNCK, POLO)
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CategoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# ==================== LEVEL 1: CATEGORY ====================

class ItemCategory(SheetDocument):
    """Level 1: Category - Broadest classification"""

    category_code: str    # 2-4 chars: APRL
    category_name: str
    description: Optional[str] = None

    item_type: str = "FG"

    # Custom Level Names for this category hierarchy
    level_names: Optional[dict] = Field(default=None)  # {"l1": "Category", "l2": "Gender", ...}

    has_color: bool = True
    has_size: bool = True
    has_fabric: bool = False
    has_brand: bool = True
    has_style: bool = True
    has_season: bool = False

    default_hsn_code: Optional[str] = None
    default_gst_rate: float = 5.0
    default_uom: str = "PCS"

    icon: str = "Package"
    color_code: str = "#10b981"
    sort_order: int = 0

    status: CategoryStatus = CategoryStatus.ACTIVE
    is_active: bool = True
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    child_count: int = 0

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_categories"
        unique_fields = ["category_code"]


# ==================== LEVEL 2: SUB-CATEGORY ====================

class ItemSubCategory(SheetDocument):
    """Level 2: Sub-Category - e.g., Men, Women, Kids"""

    sub_category_code: str    # 2-4 chars: MENS
    sub_category_name: str
    description: Optional[str] = None

    # Parent Reference
    category_code: str
    category_name: str

    path: str = ""    # APRL/MENS
    path_name: str = ""  # Apparel > Men

    # Item Type
    item_type: str = "FG"

    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None

    icon: str = "Users"
    color_code: str = "#3b82f6"
    sort_order: int = 0

    status: CategoryStatus = CategoryStatus.ACTIVE
    is_active: bool = True
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    child_count: int = 0

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_sub_categories"
        unique_fields = ["sub_category_code"]


# ==================== LEVEL 3: DIVISION ====================

class ItemDivision(SheetDocument):
    """Level 3: Division - e.g., Topwear, Bottomwear"""

    division_code: str    # 2-4 chars: TOPW
    division_name: str
    description: Optional[str] = None

    # Parent References
    category_code: str
    category_name: str
    sub_category_code: str
    sub_category_name: str

    path: str = ""    # APRL/MENS/TOPW
    path_name: str = ""  # Apparel > Men > Topwear

    # Item Type
    item_type: str = "FG"

    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None

    icon: str = "Layers"
    color_code: str = "#8b5cf6"
    sort_order: int = 0

    status: CategoryStatus = CategoryStatus.ACTIVE
    is_active: bool = True
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    child_count: int = 0

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_divisions"
        unique_fields = ["division_code"]


# ==================== LEVEL 4: CLASS ====================

class ItemClass(SheetDocument):
    """Level 4: Class - e.g., T-Shirts, Shirts, Jeans"""

    class_code: str    # 2-4 chars: TSHT
    class_name: str
    description: Optional[str] = None

    # Parent References
    category_code: str
    category_name: str
    sub_category_code: str
    sub_category_name: str
    division_code: str
    division_name: str

    path: str = ""    # APRL/MENS/TOPW/TSHT
    path_name: str = ""  # Apparel > Men > Topwear > T-Shirts

    # Item Type
    item_type: str = "FG"

    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None

    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None

    icon: str = "Tag"
    color_code: str = "#ec4899"
    sort_order: int = 0

    status: CategoryStatus = CategoryStatus.ACTIVE
    is_active: bool = True
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    child_count: int = 0

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_classes"
        unique_fields = ["class_code"]


# ==================== LEVEL 5: SUB-CLASS ====================

class ItemSubClass(SheetDocument):
    """Level 5: Sub-Class - e.g., Round Neck, V-Neck, Polo"""

    sub_class_code: str    # 2-4 chars: RNCK
    sub_class_name: str
    description: Optional[str] = None

    # Parent References (Full hierarchy)
    category_code: str
    category_name: str
    sub_category_code: str
    sub_category_name: str
    division_code: str
    division_name: str
    class_code: str
    class_name: str

    path: str = ""    # APRL/MENS/TOPW/TSHT/RNCK
    path_name: str = ""  # Apparel > Men > Topwear > T-Shirts > Round Neck

    # Item Type
    item_type: str = "FG"

    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None

    # SKU Generation
    sku_prefix: str = ""  # Prefix for SKU generation (defaults to sub_class_code)
    last_sequence: str = "A0000"  # Last used sequence for SKU generation

    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None

    icon: str = "Hash"
    color_code: str = "#f59e0b"
    sort_order: int = 0

    status: CategoryStatus = CategoryStatus.ACTIVE
    is_active: bool = True
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    item_count: int = 0

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_sub_classes"
        unique_fields = ["sub_class_code"]


# ==================== REQUEST SCHEMAS ====================

def validate_4char_code(v):
    if len(v) < 2 or len(v) > 4:
        raise ValueError('Code must be 2-4 characters')
    if not v.isalnum():
        raise ValueError('Code must be alphanumeric')
    return v.upper()


class ItemCategoryCreate(BaseModel):
    category_code: str = Field(..., min_length=2, max_length=4)
    category_name: str
    description: Optional[str] = None
    item_type: str = "FG"
    level_names: Optional[dict] = None  # {"l1": "Category", "l2": "Gender", ...}
    has_color: bool = True
    has_size: bool = True
    has_fabric: bool = False
    has_brand: bool = True
    has_style: bool = True
    has_season: bool = False
    default_hsn_code: Optional[str] = None
    default_gst_rate: float = 5.0
    default_uom: str = "PCS"
    icon: str = "Package"
    color_code: str = "#10b981"
    sort_order: int = 0

    @field_validator('category_code')
    @classmethod
    def validate_code(cls, v):
        return validate_4char_code(v)


class ItemSubCategoryCreate(BaseModel):
    sub_category_code: str = Field(..., min_length=2, max_length=4)
    sub_category_name: str
    description: Optional[str] = None
    category_code: str    # Parent
    item_type: str = "FG"
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    icon: str = "Users"
    color_code: str = "#3b82f6"
    sort_order: int = 0
    
    @field_validator('sub_category_code', 'category_code')
    @classmethod
    def validate_code(cls, v):
        return validate_4char_code(v)


class ItemDivisionCreate(BaseModel):
    division_code: str = Field(..., min_length=2, max_length=4)
    division_name: str
    description: Optional[str] = None
    category_code: str
    sub_category_code: str
    item_type: str = "FG"
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    icon: str = "Layers"
    color_code: str = "#8b5cf6"
    sort_order: int = 0
    
    @field_validator('division_code', 'category_code', 'sub_category_code')
    @classmethod
    def validate_code(cls, v):
        return validate_4char_code(v)


class ItemClassCreate(BaseModel):
    class_code: str = Field(..., min_length=2, max_length=4)
    class_name: str
    description: Optional[str] = None
    category_code: str
    sub_category_code: str
    division_code: str
    item_type: str = "FG"
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    icon: str = "Tag"
    color_code: str = "#ec4899"
    sort_order: int = 0
    
    @field_validator('class_code', 'category_code', 'sub_category_code', 'division_code')
    @classmethod
    def validate_code(cls, v):
        return validate_4char_code(v)


class ItemSubClassCreate(BaseModel):
    sub_class_code: str = Field(..., min_length=2, max_length=4)
    sub_class_name: str
    description: Optional[str] = None
    category_code: str
    sub_category_code: str
    division_code: str
    class_code: str
    item_type: str = "FG"
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    icon: str = "Hash"
    color_code: str = "#f59e0b"
    sort_order: int = 0
    
    @field_validator('sub_class_code', 'category_code', 'sub_category_code', 'division_code', 'class_code')
    @classmethod
    def validate_code(cls, v):
        return validate_4char_code(v)


# ==================== UPDATE SCHEMAS ====================

class ItemCategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    level_names: Optional[dict] = None  # {"l1": "Category", "l2": "Gender", ...}
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    has_brand: Optional[bool] = None
    has_style: Optional[bool] = None
    has_season: Optional[bool] = None
    default_hsn_code: Optional[str] = None
    default_gst_rate: Optional[float] = None
    default_uom: Optional[str] = None
    icon: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ItemSubCategoryUpdate(BaseModel):
    sub_category_name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    icon: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ItemDivisionUpdate(BaseModel):
    division_name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    icon: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ItemClassUpdate(BaseModel):
    class_name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    icon: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ItemSubClassUpdate(BaseModel):
    sub_class_name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    has_color: Optional[bool] = None
    has_size: Optional[bool] = None
    has_fabric: Optional[bool] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    icon: Optional[str] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


# ==================== RESPONSE SCHEMAS ====================

class CategoryResponse(BaseModel):
    id: str
    level: int = 1
    code: str
    name: str
    description: Optional[str]
    path: str
    path_name: str
    parent_code: Optional[str] = None
    parent_name: Optional[str] = None
    icon: str
    color_code: str
    sort_order: int
    is_active: bool
    child_count: int = 0
    created_at: datetime
    updated_at: datetime


class HierarchyTreeNode(BaseModel):
    level: int
    code: str
    name: str
    path: str
    icon: str
    color_code: str
    is_active: bool
    child_count: int
    children: List["HierarchyTreeNode"] = []


HierarchyTreeNode.model_rebuild()


# ==================== SEED DATA ====================

SEED_CATEGORIES = [
    {"category_code": "APRL", "category_name": "Apparel", "description": "All clothing and garments", "item_type": "FG", "has_color": True, "has_size": True, "has_fabric": True, "default_hsn_code": "6109", "default_gst_rate": 5.0, "icon": "Shirt", "color_code": "#10b981", "sort_order": 1},
    {"category_code": "FABR", "category_name": "Fabrics", "description": "Grey and dyed fabrics", "item_type": "GF", "has_color": True, "has_size": False, "has_fabric": True, "default_hsn_code": "5407", "default_gst_rate": 5.0, "icon": "Layers", "color_code": "#3b82f6", "sort_order": 2},
    {"category_code": "TRIM", "category_name": "Trims & Notions", "description": "Buttons, zippers, labels", "item_type": "TR", "has_color": True, "has_size": True, "default_hsn_code": "9606", "default_gst_rate": 12.0, "icon": "Sparkles", "color_code": "#f59e0b", "sort_order": 3},
    {"category_code": "YARN", "category_name": "Yarns & Fibers", "description": "Cotton, polyester yarns", "item_type": "YN", "has_color": True, "default_hsn_code": "5205", "default_gst_rate": 5.0, "icon": "Circle", "color_code": "#ec4899", "sort_order": 4},
    {"category_code": "CHEM", "category_name": "Dyes & Chemicals", "description": "Dyes, softeners", "item_type": "DY", "has_color": False, "has_size": False, "default_hsn_code": "3204", "default_gst_rate": 18.0, "icon": "FlaskConical", "color_code": "#ef4444", "sort_order": 5},
    {"category_code": "PACK", "category_name": "Packaging", "description": "Polybags, cartons, tags", "item_type": "PK", "has_color": False, "default_hsn_code": "3923", "default_gst_rate": 18.0, "icon": "Box", "color_code": "#06b6d4", "sort_order": 6},
    {"category_code": "CONS", "category_name": "Consumables", "description": "Needles, oil, tools", "item_type": "CS", "has_color": False, "has_size": False, "default_hsn_code": "8452", "default_gst_rate": 18.0, "icon": "Wrench", "color_code": "#64748b", "sort_order": 7},
]

SEED_SUB_CATEGORIES = [
    {"sub_category_code": "MENS", "sub_category_name": "Men", "category_code": "APRL", "icon": "User", "color_code": "#3b82f6", "sort_order": 1},
    {"sub_category_code": "WMNS", "sub_category_name": "Women", "category_code": "APRL", "icon": "User", "color_code": "#ec4899", "sort_order": 2},
    {"sub_category_code": "KIDS", "sub_category_name": "Kids", "category_code": "APRL", "icon": "Baby", "color_code": "#f59e0b", "sort_order": 3},
    {"sub_category_code": "UNSX", "sub_category_name": "Unisex", "category_code": "APRL", "icon": "Users", "color_code": "#8b5cf6", "sort_order": 4},
]

SEED_DIVISIONS = [
    {"division_code": "TOPW", "division_name": "Topwear", "category_code": "APRL", "sub_category_code": "MENS", "icon": "Shirt", "color_code": "#10b981", "sort_order": 1},
    {"division_code": "BTMW", "division_name": "Bottomwear", "category_code": "APRL", "sub_category_code": "MENS", "icon": "Minus", "color_code": "#3b82f6", "sort_order": 2},
    {"division_code": "OUTR", "division_name": "Outerwear", "category_code": "APRL", "sub_category_code": "MENS", "icon": "Wind", "color_code": "#6b7280", "sort_order": 3},
    {"division_code": "INNR", "division_name": "Innerwear", "category_code": "APRL", "sub_category_code": "MENS", "icon": "Shield", "color_code": "#f97316", "sort_order": 4},
]

SEED_CLASSES = [
    {"class_code": "TSHT", "class_name": "T-Shirts", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "icon": "Shirt", "color_code": "#10b981", "sort_order": 1},
    {"class_code": "SHRT", "class_name": "Shirts", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "icon": "Shirt", "color_code": "#3b82f6", "sort_order": 2},
    {"class_code": "POLO", "class_name": "Polo Shirts", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "icon": "Shirt", "color_code": "#8b5cf6", "sort_order": 3},
    {"class_code": "HOOD", "class_name": "Hoodies", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "icon": "Shirt", "color_code": "#ef4444", "sort_order": 4},
    {"class_code": "SWTR", "class_name": "Sweaters", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "icon": "Shirt", "color_code": "#f59e0b", "sort_order": 5},
    {"class_code": "JEAN", "class_name": "Jeans", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "BTMW", "icon": "Minus", "color_code": "#3b82f6", "sort_order": 1},
    {"class_code": "TROU", "class_name": "Trousers", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "BTMW", "icon": "Minus", "color_code": "#6b7280", "sort_order": 2},
    {"class_code": "SHRTS", "class_name": "Shorts", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "BTMW", "icon": "Minus", "color_code": "#10b981", "sort_order": 3},
]

SEED_SUB_CLASSES = [
    {"sub_class_code": "RNCK", "sub_class_name": "Round Neck", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "class_code": "TSHT", "icon": "Circle", "color_code": "#10b981", "sort_order": 1},
    {"sub_class_code": "VNCK", "sub_class_name": "V-Neck", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "class_code": "TSHT", "icon": "ChevronDown", "color_code": "#3b82f6", "sort_order": 2},
    {"sub_class_code": "HENL", "sub_class_name": "Henley", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "class_code": "TSHT", "icon": "MoreVertical", "color_code": "#8b5cf6", "sort_order": 3},
    {"sub_class_code": "OVRS", "sub_class_name": "Oversized", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "class_code": "TSHT", "icon": "Maximize", "color_code": "#f59e0b", "sort_order": 4},
    {"sub_class_code": "CROP", "sub_class_name": "Crop Top", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "TOPW", "class_code": "TSHT", "icon": "Minimize", "color_code": "#ec4899", "sort_order": 5},
    {"sub_class_code": "SLMF", "sub_class_name": "Slim Fit", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "BTMW", "class_code": "JEAN", "icon": "Minus", "color_code": "#3b82f6", "sort_order": 1},
    {"sub_class_code": "RGLF", "sub_class_name": "Regular Fit", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "BTMW", "class_code": "JEAN", "icon": "Square", "color_code": "#6b7280", "sort_order": 2},
    {"sub_class_code": "SKNF", "sub_class_name": "Skinny Fit", "category_code": "APRL", "sub_category_code": "MENS", "division_code": "BTMW", "class_code": "JEAN", "icon": "Minus", "color_code": "#10b981", "sort_order": 3},
]
