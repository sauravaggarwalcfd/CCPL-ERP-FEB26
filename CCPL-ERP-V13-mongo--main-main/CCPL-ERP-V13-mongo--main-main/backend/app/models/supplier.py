from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BankDetails(BaseModel):
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_type: Optional[str] = None


class Supplier(SheetDocument):
    code: str  # SUP-001
    company_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: str
    alternate_phone: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None

    address: dict = {}  # {line1, line2, city, state, pincode, country}
    bank_details: BankDetails = BankDetails()

    payment_terms: int = 30  # Days
    credit_limit: float = 0
    outstanding_balance: float = 0

    notes: Optional[str] = None
    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_suppliers_legacy"
        unique_fields = ["code"]
