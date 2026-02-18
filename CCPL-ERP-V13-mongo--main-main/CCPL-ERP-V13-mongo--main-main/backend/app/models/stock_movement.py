from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MovementType(str, Enum):
    PURCHASE_IN = "PURCHASE_IN"
    SALE_OUT = "SALE_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    ADJUSTMENT_ADD = "ADJUSTMENT_ADD"
    ADJUSTMENT_REMOVE = "ADJUSTMENT_REMOVE"
    RETURN_IN = "RETURN_IN"
    DAMAGE_OUT = "DAMAGE_OUT"
    OPENING_STOCK = "OPENING_STOCK"


class MovementReference(BaseModel):
    type: str  # purchase_order, sale_order, transfer, adjustment
    id: str
    number: str  # PO-2024-0001


class EmbeddedUser(BaseModel):
    id: str
    name: str


class StockMovement(SheetDocument):
    variant: dict  # {id, sku, product_name, color, size}
    warehouse: dict  # {id, code, name}

    movement_type: MovementType
    reference: Optional[MovementReference] = None

    quantity: int
    before_quantity: Optional[int] = None
    after_quantity: Optional[int] = None
    unit_cost: Optional[float] = None

    notes: Optional[str] = None
    created_by: Optional[EmbeddedUser] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_stock_movements"
        unique_fields = []
