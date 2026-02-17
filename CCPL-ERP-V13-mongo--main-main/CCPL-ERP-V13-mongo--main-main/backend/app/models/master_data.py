from .sheet_document import SheetDocument
from pydantic import Field
from typing import Optional
from datetime import datetime


class Category(SheetDocument):
    name: str
    slug: str
    parent_id: Optional[str] = None
    parent_name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class SheetSettings:
        tab_name = "_md_categories"
        unique_fields = ["slug"]


class Brand(SheetDocument):
    name: str
    slug: str
    logo: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class SheetSettings:
        tab_name = "_md_brands"
        unique_fields = ["name"]


class Season(SheetDocument):
    name: str  # SS24, AW24
    full_name: Optional[str] = None  # Spring/Summer 2024
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class SheetSettings:
        tab_name = "_md_seasons"
        unique_fields = ["name"]


class Color(SheetDocument):
    name: str
    code: str  # BLK, WHT
    hex: Optional[str] = None  # #000000
    is_active: bool = True
    sort_order: int = 0

    class SheetSettings:
        tab_name = "_md_colors"
        unique_fields = ["code"]


class Size(SheetDocument):
    name: str  # XS, S, M, L, XL or 28, 30, 32
    type: str = "apparel"  # apparel, footwear, accessories
    sort_order: int = 0
    is_active: bool = True

    class SheetSettings:
        tab_name = "_md_sizes"
        unique_fields = ["name"]
