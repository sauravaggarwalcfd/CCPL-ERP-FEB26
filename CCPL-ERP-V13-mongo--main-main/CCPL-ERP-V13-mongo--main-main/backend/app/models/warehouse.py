from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"


class Contact(BaseModel):
    person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class WarehouseLocation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # A-01-01 (Aisle-Rack-Shelf)
    name: Optional[str] = None
    type: str = "shelf"  # shelf, bin, floor, staging
    capacity: Optional[int] = None
    is_active: bool = True


class Warehouse(SheetDocument):
    code: str  # WH-MUM-01
    name: str
    address: Address = Address()
    contact: Contact = Contact()
    locations: List[WarehouseLocation] = []
    is_active: bool = True
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class SheetSettings:
        tab_name = "_warehouses"
        unique_fields = ["code"]
