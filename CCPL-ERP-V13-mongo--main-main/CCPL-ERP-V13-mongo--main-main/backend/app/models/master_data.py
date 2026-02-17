from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime


class Category(Document):
    name: str
    slug: Indexed(str, unique=True)
    parent_id: Optional[str] = None
    parent_name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "categories"


class Brand(Document):
    name: Indexed(str, unique=True)
    slug: Indexed(str, unique=True)
    logo: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "brands"


class Season(Document):
    name: str  # SS24, AW24
    full_name: Optional[str] = None  # Spring/Summer 2024
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "seasons"


class Color(Document):
    name: str
    code: Indexed(str, unique=True)  # BLK, WHT
    hex: Optional[str] = None  # #000000
    is_active: bool = True
    sort_order: int = 0

    class Settings:
        name = "colors"


class Size(Document):
    name: str  # XS, S, M, L, XL or 28, 30, 32
    type: str = "apparel"  # apparel, footwear, accessories
    sort_order: int = 0
    is_active: bool = True

    class Settings:
        name = "sizes"
