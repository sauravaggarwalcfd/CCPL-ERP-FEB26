from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class TransferStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransferItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product: dict  # {id, style_number, name}
    variant: dict  # {id, sku, color, size}
    requested_quantity: int
    shipped_quantity: int = 0
    received_quantity: int = 0
    notes: Optional[str] = None


class StockTransfer(SheetDocument):
    transfer_number: str  # TRF-2024-0001

    from_warehouse: dict  # {id, code, name}
    to_warehouse: dict  # {id, code, name}

    status: TransferStatus = TransferStatus.DRAFT

    items: List[TransferItem] = []

    notes: Optional[str] = None

    created_by: Optional[dict] = None
    approved_by: Optional[dict] = None
    approved_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    received_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_transfers"
        unique_fields = ["transfer_number"]
