"""
Brand Master Model
Stores information about brands used/sold in the business
"""

from beanie import Document
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class BrandMaster(Document):
    """Brand Master collection model"""

    brand_code: str = Field(..., unique=True, index=True)
    brand_name: str = Field(..., index=True)
    brand_category: Optional[str] = None  # Textile/Trim/Button/etc
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name = "brand_master"
        indexes = [
            "brand_code",
            "brand_name",
            "is_active",
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "brand_code": "BR-001",
                "brand_name": "ABC Threads",
                "brand_category": "Textile",
                "country": "India",
                "contact_person": "John Doe",
                "email": "john@abc.com",
                "phone": "+91-9999999999",
                "website": "www.abc.com",
                "is_active": True
            }
        }


class BrandMasterCreate(BaseModel):
    """Schema for creating a brand"""
    brand_code: str = Field(..., min_length=2, max_length=20)
    brand_name: str = Field(..., min_length=2, max_length=200)
    brand_category: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True


class BrandMasterUpdate(BaseModel):
    """Schema for updating a brand"""
    brand_name: Optional[str] = None
    brand_category: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class BrandMasterResponse(BaseModel):
    """Schema for brand response"""
    id: str
    brand_code: str
    brand_name: str
    brand_category: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
