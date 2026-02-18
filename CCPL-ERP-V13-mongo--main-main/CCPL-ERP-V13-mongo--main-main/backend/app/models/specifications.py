"""
Specifications Models
Manages category-specific specifications configuration and item specification values
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FieldType(str, Enum):
    """Field types for custom fields"""
    SELECT = "SELECT"
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    CHECKBOX = "CHECKBOX"
    DATE = "DATE"
    TEXTAREA = "TEXTAREA"


class FieldSource(str, Enum):
    """Source of field values"""
    COLOUR_MASTER = "COLOUR_MASTER"
    SIZE_MASTER = "SIZE_MASTER"
    UOM_MASTER = "UOM_MASTER"
    SUPPLIER_MASTER = "SUPPLIER_MASTER"
    CUSTOM = "CUSTOM"


# ==================== CONFIGURATION SCHEMAS ====================

class VariantFieldConfig(BaseModel):
    """Configuration for a variant field (Colour, Size, UOM, Vendor)"""
    enabled: bool = False
    required: bool = False
    field_name: str
    field_type: str = "SELECT"
    field_key: str
    source: FieldSource
    groups: List[str] = []  # Filter by groups (e.g., THREAD_COLORS)
    allow_multiple: bool = False
    default_value: Optional[str] = None
    filter: Dict[str, Any] = {}  # Additional filters


class CustomFieldConfig(BaseModel):
    """Configuration for custom fields"""
    field_code: str
    field_name: str
    field_type: FieldType
    field_key: str
    enabled: bool = True
    required: bool = False
    options: List[str] = []  # For SELECT type
    default_value: Optional[Any] = None
    placeholder: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    display_order: int = 0
    validation_rules: Dict[str, Any] = {}


class SpecificationsConfig(BaseModel):
    """Complete specifications configuration"""
    colour: Optional[VariantFieldConfig] = None
    size: Optional[VariantFieldConfig] = None
    uom: Optional[VariantFieldConfig] = None
    vendor: Optional[VariantFieldConfig] = None


# ==================== DATABASE MODELS ====================

class CategorySpecifications(SheetDocument):
    """Category specifications configuration document"""
    category_code: str
    category_name: str
    category_level: int = 1  # L1, L2, L3, etc.

    # Standard variant fields configuration
    specifications: SpecificationsConfig

    # Custom fields specific to this category
    custom_fields: List[CustomFieldConfig] = []

    # Metadata
    is_active: bool = True
    created_by: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified_by: Optional[str] = None
    last_modified_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "category_specifications"
        unique_fields = ["category_code"]


class ItemSpecifications(SheetDocument):
    """Item specifications values document"""
    item_code: str
    category_code: str

    # Standard variant values
    colour_code: Optional[str] = None
    size_code: Optional[str] = None
    uom_code: Optional[str] = None
    vendor_code: Optional[str] = None

    # Custom field values (flexible dict)
    custom_field_values: Dict[str, Any] = {}

    # Metadata
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "item_specifications"
        unique_fields = ["item_code"]


# ==================== REQUEST SCHEMAS ====================

class VariantFieldConfigRequest(BaseModel):
    """Request to update variant field config"""
    enabled: bool
    required: bool = False
    groups: List[str] = []
    allow_multiple: bool = False
    default_value: Optional[str] = None


class CustomFieldConfigRequest(BaseModel):
    """Request to add/update custom field"""
    field_code: str
    field_name: str
    field_type: FieldType
    enabled: bool = True
    required: bool = False
    options: List[str] = []
    default_value: Optional[Any] = None
    placeholder: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    display_order: int = 0


class CategorySpecificationsRequest(BaseModel):
    """Request to create/update category specifications"""
    category_code: str
    category_name: str
    category_level: int = 1
    specifications: Dict[str, VariantFieldConfigRequest] = {}
    custom_fields: List[CustomFieldConfigRequest] = []


class ItemSpecificationsRequest(BaseModel):
    """Request to create/update item specifications"""
    colour_code: Optional[str] = None
    size_code: Optional[str] = None
    uom_code: Optional[str] = None
    vendor_code: Optional[str] = None
    custom_field_values: Dict[str, Any] = {}


# ==================== RESPONSE SCHEMAS ====================

class FieldOption(BaseModel):
    """Option for field dropdown"""
    code: str
    name: str
    additional_info: Dict[str, Any] = {}


class FormField(BaseModel):
    """Field definition for form rendering"""
    field_key: str
    field_name: str
    field_type: str
    required: bool = False
    enabled: bool = True
    options: List[FieldOption] = []
    default_value: Optional[Any] = None
    placeholder: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    display_order: int = 0
    source: Optional[str] = None
    groups: List[str] = []


class CategorySpecificationsResponse(BaseModel):
    """Response for category specifications"""
    id: str
    category_code: str
    category_name: str
    category_level: int
    specifications: Dict[str, Any]
    custom_fields: List[CustomFieldConfig]
    is_active: bool
    created_by: Optional[str]
    created_date: datetime
    last_modified_by: Optional[str]
    last_modified_date: datetime


class ItemSpecificationsResponse(BaseModel):
    """Response for item specifications"""
    id: str
    item_code: str
    category_code: str
    colour_code: Optional[str]
    size_code: Optional[str]
    uom_code: Optional[str]
    vendor_code: Optional[str]
    custom_field_values: Dict[str, Any]
    created_date: datetime
    last_modified_date: datetime


# ==================== HELPER FUNCTIONS ====================

def create_default_variant_field_config(
    field_key: str,
    field_name: str,
    source: FieldSource,
    enabled: bool = False,
    required: bool = False,
    groups: List[str] = []
) -> VariantFieldConfig:
    """Create default variant field configuration"""
    return VariantFieldConfig(
        enabled=enabled,
        required=required,
        field_name=field_name,
        field_type="SELECT",
        field_key=field_key,
        source=source,
        groups=groups,
        allow_multiple=False,
        default_value=None
    )


def create_default_specifications_config() -> SpecificationsConfig:
    """Create default specifications config with all fields disabled"""
    return SpecificationsConfig(
        colour=create_default_variant_field_config(
            field_key="colour_code",
            field_name="Colour",
            source=FieldSource.COLOUR_MASTER
        ),
        size=create_default_variant_field_config(
            field_key="size_code",
            field_name="Size",
            source=FieldSource.SIZE_MASTER
        ),
        uom=create_default_variant_field_config(
            field_key="uom_code",
            field_name="UOM",
            source=FieldSource.UOM_MASTER
        ),
        vendor=create_default_variant_field_config(
            field_key="vendor_code",
            field_name="Vendor/Brand",
            source=FieldSource.SUPPLIER_MASTER
        )
    )
