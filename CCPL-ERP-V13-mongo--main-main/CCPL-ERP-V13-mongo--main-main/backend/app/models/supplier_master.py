"""
Supplier Master Model
Stores information about suppliers for raw materials
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class SupplierMaster(SheetDocument):
    """Supplier Master collection model"""

    supplier_code: str = Field(..., unique=True, index=True)
    supplier_name: str = Field(..., index=True)
    supplier_type: Optional[str] = None  # Textile Supplier/Cotton Supplier/etc
    country: Optional[str] = None
    city: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None  # Net 30/Advance/COD
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "_supplier_master"
        unique_fields = ["supplier_code"]

    class Config:
        json_schema_extra = {
            "example": {
                "supplier_code": "SUP-001",
                "supplier_name": "XYZ Industries",
                "supplier_type": "Textile Supplier",
                "country": "India",
                "city": "Delhi",
                "contact_person": "Raj Kumar",
                "email": "raj@xyz.com",
                "phone": "+91-8888888888",
                "website": "www.xyz.com",
                "address": "123 Industrial Area, Delhi",
                "gst_number": "18AABCT1234H1Z5",
                "bank_account": None,
                "payment_terms": "Net 30",
                "is_active": True
            }
        }


class SupplierMasterCreate(BaseModel):
    """Schema for creating a supplier"""
    supplier_code: str = Field(..., min_length=2, max_length=20)
    supplier_name: str = Field(..., min_length=2, max_length=200)
    supplier_type: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: bool = True


class SupplierMasterUpdate(BaseModel):
    """Schema for updating a supplier"""
    supplier_name: Optional[str] = None
    supplier_type: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierMasterResponse(BaseModel):
    """Schema for supplier response"""
    id: str
    supplier_code: str
    supplier_name: str
    supplier_type: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
