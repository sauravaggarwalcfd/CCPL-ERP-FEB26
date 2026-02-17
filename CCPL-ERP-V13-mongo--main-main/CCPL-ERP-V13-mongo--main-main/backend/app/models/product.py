from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class EmbeddedCategory(BaseModel):
    id: str
    name: str
    slug: str


class EmbeddedBrand(BaseModel):
    id: str
    name: str


class EmbeddedSeason(BaseModel):
    id: str
    name: str


class Color(BaseModel):
    name: str
    code: str  # BLK, WHT, NVY
    hex: Optional[str] = None  # #000000


class Size(BaseModel):
    name: str  # S, M, L, XL or 28, 30, 32
    type: str = "apparel"  # apparel, footwear


class VariantImage(BaseModel):
    url: str
    alt: Optional[str] = None
    is_primary: bool = False


class ProductVariant(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    sku: str
    color: Color
    size: Size
    barcode: Optional[str] = None
    cost_price: float = 0
    selling_price: float = 0
    mrp: float = 0
    min_stock_level: int = 5
    max_stock_level: int = 100
    reorder_point: int = 10
    reorder_quantity: int = 20
    is_active: bool = True
    images: List[VariantImage] = []


class Product(Document):
    style_number: Indexed(str, unique=True)  # CC-TS-001
    name: str
    description: Optional[str] = None

    # References (embedded)
    category: Optional[EmbeddedCategory] = None
    subcategory: Optional[EmbeddedCategory] = None
    brand: Optional[EmbeddedBrand] = None
    season: Optional[EmbeddedSeason] = None

    # Pricing
    base_cost: float = 0
    base_price: float = 0

    # Tax
    hsn_code: Optional[str] = None
    gst_rate: float = 5.0  # 5, 12, 18

    # Details
    material: Optional[str] = None
    care_instructions: Optional[str] = None
    weight: Optional[int] = None  # grams
    tags: List[str] = []

    # Variants
    variants: List[ProductVariant] = []

    # Images
    primary_image: Optional[str] = None

    # Status
    is_active: bool = True

    # Metadata
    created_by: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "products"
        indexes = [
            "style_number",
            "category.slug",
            "brand.name",
            "variants.sku",
            "variants.barcode",
            [("name", "text"), ("style_number", "text")],
        ]
