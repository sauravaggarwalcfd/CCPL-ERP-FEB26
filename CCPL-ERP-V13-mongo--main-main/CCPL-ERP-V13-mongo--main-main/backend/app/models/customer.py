from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CustomerType(str, Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    DISTRIBUTOR = "distributor"


class CustomerAddress(BaseModel):
    type: str = "shipping"  # billing, shipping
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_default: bool = False


class Customer(SheetDocument):
    code: Optional[str] = None  # CUST-001 (for B2B)
    customer_type: CustomerType = CustomerType.RETAIL
    name: str
    email: Optional[str] = None
    phone: str
    alternate_phone: Optional[str] = None
    gst_number: Optional[str] = None

    addresses: List[CustomerAddress] = []

    credit_limit: float = 0
    outstanding_balance: float = 0
    loyalty_points: int = 0

    tags: List[str] = []
    notes: Optional[str] = None
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customers"
        unique_fields = ["code"]
