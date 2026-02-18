"""
Item Master Model - Legacy Support
Note: The 5-level hierarchy (ItemCategory, ItemSubCategory, ItemDivision, ItemClass, ItemSubClass)
is now in category_hierarchy.py
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InventoryType(str, Enum):
    STOCKED = "stocked"
    NON_STOCKED = "non_stocked"
    CONSUMABLE = "consumable"


# ==================== ITEM MASTER ====================
class ItemMaster(SheetDocument):
    """
    Item Master Document
    References the 5-level hierarchy from category_hierarchy.py
    """
    item_code: str  # TSHRT-M-BLUE-001
    item_name: str  # Men's Basic Crew Neck T-Shirt - Blue (Medium)
    item_description: Optional[str] = None

    # 5-Level Hierarchy Links
    category_code: str  # Level 1 - e.g., CLOTH
    category_name: str  # Clothing - Denormalized
    
    sub_category_code: Optional[str] = None  # Level 2 - e.g., MEN
    sub_category_name: Optional[str] = None
    
    division_code: Optional[str] = None  # Level 3 - e.g., MFRML
    division_name: Optional[str] = None
    
    class_code: Optional[str] = None  # Level 4 - e.g., MSHRT
    class_name: Optional[str] = None
    
    sub_class_code: Optional[str] = None  # Level 5 - e.g., MSHRTP
    sub_class_name: Optional[str] = None
    
    # Full hierarchy path
    hierarchy_path: Optional[str] = None  # CLOTH/MEN/MFRML/MSHRT/MSHRTP
    hierarchy_path_name: Optional[str] = None  # Clothing > Men > Formal > Shirts > Polo
    
    # Item Attributes
    color_id: Optional[str] = None
    color_name: Optional[str] = None
    
    size_id: Optional[str] = None
    size_name: Optional[str] = None
    
    brand_id: Optional[str] = None
    brand_name: Optional[str] = None
    
    # UOM and Inventory
    uom: str = "PCS"
    inventory_type: InventoryType = InventoryType.STOCKED
    
    # Pricing
    cost_price: float = 0.0
    selling_price: float = 0.0
    mrp: float = 0.0
    
    # Tax Information
    hsn_code: Optional[str] = None
    gst_rate: float = 5.0
    
    # Warehouse & Stock Management
    warehouse_id: Optional[str] = None
    warehouse_name: Optional[str] = None
    bin_location: Optional[str] = None
    
    # Stock Levels
    min_stock_level: int = 5
    max_stock_level: int = 100
    reorder_point: int = 10
    reorder_quantity: int = 20
    current_stock: int = 0
    
    # Additional Details
    material: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[dict] = None
    care_instructions: Optional[str] = None
    barcode: Optional[str] = None
    serial_tracked: bool = False
    batch_tracked: bool = True

    # Image Information (linked to FileMaster)
    image_id: Optional[str] = None  # FILE-YYYYMMDD-XXXX
    image_url: Optional[str] = None  # /uploads/images/filename.jpg
    image_name: Optional[str] = None  # Original filename
    thumbnail_url: Optional[str] = None  # /uploads/thumbnails/thumb_filename.jpg

    # BASE64 Image Storage (alternative to file storage)
    image_base64: Optional[str] = None  # Base64 encoded image data
    image_type: Optional[str] = None  # MIME type (image/jpeg, image/png, etc.)
    image_size: Optional[int] = None  # Size in bytes

    # Status
    is_active: bool = True
    discontinued: bool = False
    discontinued_date: Optional[datetime] = None
    deleted_at: Optional[datetime] = None  # Soft delete timestamp
    deleted_by: Optional[str] = None  # Who deleted it
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "item_master"
        unique_fields = ["item_code"]


# ==================== REQUEST/RESPONSE SCHEMAS ====================
class ItemMasterCreate(BaseModel):
    item_code: str
    item_name: str
    item_description: Optional[str] = None
    category_code: str
    category_name: str
    sub_category_code: Optional[str] = None
    sub_category_name: Optional[str] = None
    division_code: Optional[str] = None
    division_name: Optional[str] = None
    class_code: Optional[str] = None
    class_name: Optional[str] = None
    sub_class_code: Optional[str] = None
    sub_class_name: Optional[str] = None
    color_id: Optional[str] = None
    color_name: Optional[str] = None
    size_id: Optional[str] = None
    size_name: Optional[str] = None
    brand_id: Optional[str] = None
    brand_name: Optional[str] = None
    uom: str = "PCS"
    inventory_type: InventoryType = InventoryType.STOCKED
    cost_price: float = 0.0
    selling_price: float = 0.0
    mrp: float = 0.0
    hsn_code: Optional[str] = None
    gst_rate: float = 5.0
    warehouse_id: Optional[str] = None
    warehouse_name: Optional[str] = None
    barcode: Optional[str] = None
    image_id: Optional[str] = None
    image_url: Optional[str] = None
    image_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_base64: Optional[str] = None
    image_type: Optional[str] = None
    image_size: Optional[int] = None


class ItemMasterUpdate(BaseModel):
    item_name: Optional[str] = None
    item_description: Optional[str] = None
    color_id: Optional[str] = None
    color_name: Optional[str] = None
    size_id: Optional[str] = None
    size_name: Optional[str] = None
    brand_id: Optional[str] = None
    brand_name: Optional[str] = None
    uom: Optional[str] = None
    inventory_type: Optional[InventoryType] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    warehouse_id: Optional[str] = None
    warehouse_name: Optional[str] = None
    barcode: Optional[str] = None
    image_id: Optional[str] = None
    image_url: Optional[str] = None
    image_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_base64: Optional[str] = None
    image_type: Optional[str] = None
    image_size: Optional[int] = None
    is_active: Optional[bool] = None


class ItemMasterResponse(BaseModel):
    id: str
    item_code: str
    item_name: str
    item_description: Optional[str]
    category_code: str
    category_name: str
    sub_category_code: Optional[str]
    sub_category_name: Optional[str]
    division_code: Optional[str]
    division_name: Optional[str]
    class_code: Optional[str]
    class_name: Optional[str]
    sub_class_code: Optional[str]
    sub_class_name: Optional[str]
    hierarchy_path: Optional[str]
    hierarchy_path_name: Optional[str]
    uom: str
    cost_price: float
    selling_price: float
    mrp: float
    hsn_code: Optional[str]
    gst_rate: float
    current_stock: int
    image_id: Optional[str] = None
    image_url: Optional[str] = None
    image_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_base64: Optional[str] = None
    image_type: Optional[str] = None
    image_size: Optional[int] = None
    is_active: bool
