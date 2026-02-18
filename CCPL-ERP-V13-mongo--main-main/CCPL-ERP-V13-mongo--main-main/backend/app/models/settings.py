from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CompanyInfo(BaseModel):
    name: str = "Confidence Clothing"
    logo: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: dict = {}
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class InvoiceSettings(BaseModel):
    prefix: str = "INV"
    terms_conditions: Optional[str] = None
    footer_note: Optional[str] = None


class Sequences(BaseModel):
    product: int = 0
    purchase_order: int = 0
    sale_order: int = 0
    transfer: int = 0
    adjustment: int = 0
    customer: int = 0
    supplier: int = 0


class Defaults(BaseModel):
    warehouse_id: Optional[str] = None
    gst_rate: float = 5.0
    currency: str = "INR"


class AppSettings(SheetDocument):
    company: CompanyInfo = CompanyInfo()
    invoice: InvoiceSettings = InvoiceSettings()
    sequences: Sequences = Sequences()
    defaults: Defaults = Defaults()
    stock_valuation: str = "weighted_average"  # fifo, weighted_average

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "_settings"
        unique_fields = []
