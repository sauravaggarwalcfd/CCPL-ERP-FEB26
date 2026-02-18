"""
Colour Master Model
Manages colour variants with grouping system
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class ColourGroup(str, Enum):
    """Pre-defined colour groups"""
    THREAD_COLORS = "THREAD_COLORS"
    FABRIC_COLORS = "FABRIC_COLORS"
    BUTTON_COLORS = "BUTTON_COLORS"
    LABEL_COLORS = "LABEL_COLORS"
    OTHER = "OTHER"


class RGBValue(BaseModel):
    """RGB colour representation"""
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)


class ColourMaster(SheetDocument):
    """Colour Master Document"""
    colour_code: str
    colour_name: str
    colour_hex: str  # #RRGGBB format
    rgb_value: RGBValue
    colour_group: str  # Changed from Enum to str to allow dynamic groups
    group_name: str  # Display name
    is_active: bool = True
    display_order: int = 0
    description: Optional[str] = None

    # Audit fields
    created_by: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified_by: Optional[str] = None
    last_modified_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_colour_master"
        unique_fields = ["colour_code"]


# ==================== REQUEST SCHEMAS ====================

class ColourCreate(BaseModel):
    colour_code: str = Field(..., min_length=2, max_length=20)
    colour_name: str
    colour_hex: str  # Must be #RRGGBB format
    colour_group: str
    description: Optional[str] = None
    display_order: int = 0

    @field_validator('colour_code')
    @classmethod
    def validate_code(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Code must be alphanumeric (with - or _ allowed)')
        return v.upper()

    @field_validator('colour_hex')
    @classmethod
    def validate_hex(cls, v):
        if not v.startswith('#'):
            v = '#' + v
        if len(v) != 7:
            raise ValueError('Hex colour must be in #RRGGBB format')
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError('Invalid hex colour format')
        return v.upper()


class ColourUpdate(BaseModel):
    colour_name: Optional[str] = None
    colour_hex: Optional[str] = None
    colour_group: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('colour_hex')
    @classmethod
    def validate_hex(cls, v):
        if v is None:
            return v
        if not v.startswith('#'):
            v = '#' + v
        if len(v) != 7:
            raise ValueError('Hex colour must be in #RRGGBB format')
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError('Invalid hex colour format')
        return v.upper()


class ColourResponse(BaseModel):
    id: str
    colour_code: str
    colour_name: str
    colour_hex: str
    rgb_value: RGBValue
    colour_group: str
    group_name: str
    is_active: bool
    display_order: int
    description: Optional[str]
    created_by: Optional[str]
    created_date: datetime
    last_modified_by: Optional[str]
    last_modified_date: datetime


# ==================== GROUP DISPLAY NAMES ====================

COLOUR_GROUP_NAMES = {
    ColourGroup.THREAD_COLORS: "Thread Colors",
    ColourGroup.FABRIC_COLORS: "Fabric Colors",
    ColourGroup.BUTTON_COLORS: "Button Colors",
    ColourGroup.LABEL_COLORS: "Label Colors",
    ColourGroup.OTHER: "Other Colors"
}


# ==================== HELPER FUNCTIONS ====================

def hex_to_rgb(hex_colour: str) -> RGBValue:
    """Convert hex colour to RGB"""
    hex_colour = hex_colour.lstrip('#')
    return RGBValue(
        r=int(hex_colour[0:2], 16),
        g=int(hex_colour[2:4], 16),
        b=int(hex_colour[4:6], 16)
    )


def rgb_to_hex(rgb: RGBValue) -> str:
    """Convert RGB to hex colour"""
    return f"#{rgb.r:02X}{rgb.g:02X}{rgb.b:02X}"
