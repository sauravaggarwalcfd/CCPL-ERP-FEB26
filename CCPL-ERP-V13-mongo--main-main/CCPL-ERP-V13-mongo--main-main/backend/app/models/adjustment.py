from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class AdjustmentType(str, Enum):
    CYCLE_COUNT = "cycle_count"
    DAMAGE = "damage"
    THEFT = "theft"
    FOUND = "found"
    EXPIRY = "expiry"
    OTHER = "other"


class AdjustmentStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class AdjustmentItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product: dict  # {id, style_number, name}
    variant: dict  # {id, sku, color, size}
    system_quantity: int
    actual_quantity: int
    variance: int = 0  # actual - system
    unit_cost: Optional[float] = None
    notes: Optional[str] = None


class StockAdjustment(SheetDocument):
    adjustment_number: str  # ADJ-2024-0001

    warehouse: dict  # {id, code, name}
    adjustment_type: AdjustmentType
    status: AdjustmentStatus = AdjustmentStatus.DRAFT

    items: List[AdjustmentItem] = []

    reason: Optional[str] = None

    created_by: Optional[dict] = None
    approved_by: Optional[dict] = None
    approved_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "stock_adjustments"
        unique_fields = ["adjustment_number"]
