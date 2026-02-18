from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"


class SOItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product: dict  # {id, style_number, name}
    variant: dict  # {id, sku, color, size, barcode}
    quantity: int
    unit_price: float
    tax_rate: float = 0
    tax_amount: float = 0
    discount_percent: float = 0
    total_amount: float


class EmbeddedCustomer(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str] = None
    gst_number: Optional[str] = None


class SaleOrder(SheetDocument):
    order_number: str  # SO-2024-0001

    customer: EmbeddedCustomer
    warehouse: dict  # {id, code, name}

    status: OrderStatus = OrderStatus.PENDING

    order_date: datetime = Field(default_factory=datetime.utcnow)

    shipping_address: dict = {}
    billing_address: dict = {}

    items: List[SOItem] = []

    subtotal: float = 0
    tax_amount: float = 0
    discount_amount: float = 0
    shipping_cost: float = 0
    total_amount: float = 0

    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_method: Optional[str] = None  # cash, card, upi, credit
    paid_amount: float = 0

    notes: Optional[str] = None

    created_by: Optional[dict] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "sale_orders"
        unique_fields = ["order_number"]
