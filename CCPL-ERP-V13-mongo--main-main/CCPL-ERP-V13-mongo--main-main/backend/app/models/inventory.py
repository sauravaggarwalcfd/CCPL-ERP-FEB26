from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmbeddedProduct(BaseModel):
    id: str
    style_number: str
    name: str


class EmbeddedVariant(BaseModel):
    id: str
    sku: str
    barcode: Optional[str] = None
    color: str
    size: str


class EmbeddedWarehouse(BaseModel):
    id: str
    code: str
    name: str


class EmbeddedLocation(BaseModel):
    id: str
    code: str


class Inventory(SheetDocument):
    product: EmbeddedProduct
    variant: EmbeddedVariant
    warehouse: EmbeddedWarehouse
    location: Optional[EmbeddedLocation] = None

    quantity: int = 0
    reserved_quantity: int = 0
    cost_price: float = 0

    last_counted_at: Optional[datetime] = None
    last_counted_by: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    class Settings:
        name = "_inventory"
        unique_fields = []
