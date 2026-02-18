"""
File Master Model
Stores metadata for uploaded files (images, documents, etc.)
"""

from .sheet_document import SheetDocument
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class FileCategory(str, Enum):
    """Categories for organizing files"""
    ITEM_IMAGE = "item_image"
    PRODUCT_IMAGE = "product_image"
    DOCUMENT = "document"
    LOGO = "logo"
    BANNER = "banner"
    OTHER = "other"


class FileMaster(SheetDocument):
    """File Master collection model for storing file metadata"""

    # Unique file identifier (FILE-YYYYMMDD-XXXX format)
    file_id: str = Field(..., unique=True, index=True)

    # File information
    file_name: str = Field(..., index=True)  # Stored filename (unique, sanitized)
    original_name: str  # Original uploaded filename
    file_type: str  # MIME type (e.g., image/jpeg)
    file_extension: str  # File extension (e.g., .jpg)
    file_size: int  # Size in bytes

    # Storage paths
    file_path: str  # Relative path from uploads folder
    file_url: str  # Full URL to access the file
    thumbnail_path: Optional[str] = None  # Path to thumbnail (if image)
    thumbnail_url: Optional[str] = None  # URL to thumbnail

    # Organization
    category: FileCategory = Field(default=FileCategory.OTHER)
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    # Image metadata (for images only)
    width: Optional[int] = None
    height: Optional[int] = None

    # Audit fields
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: Optional[str] = None
    uploaded_by_name: Optional[str] = None

    # Soft delete
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "file_master"
        unique_fields = ["file_id"]

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "FILE-20250122-0001",
                "file_name": "product_image_001.jpg",
                "original_name": "My Product Photo.jpg",
                "file_type": "image/jpeg",
                "file_extension": ".jpg",
                "file_size": 245678,
                "file_path": "images/product_image_001.jpg",
                "file_url": "/uploads/images/product_image_001.jpg",
                "category": "item_image",
                "description": "Main product image",
                "width": 1920,
                "height": 1080,
            }
        }


# ==================== REQUEST/RESPONSE SCHEMAS ====================

class FileUploadResponse(BaseModel):
    """Response schema for file upload"""
    id: str
    file_id: str
    file_name: str
    original_name: str
    file_type: str
    file_size: int
    file_url: str
    thumbnail_url: Optional[str] = None
    category: str
    upload_date: datetime
    message: str


class FileListResponse(BaseModel):
    """Response schema for file listing"""
    id: str
    file_id: str
    file_name: str
    original_name: str
    file_type: str
    file_size: int
    file_url: str
    thumbnail_url: Optional[str] = None
    category: str
    description: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    upload_date: datetime
    uploaded_by_name: Optional[str] = None


class FileDetailResponse(BaseModel):
    """Response schema for file details"""
    id: str
    file_id: str
    file_name: str
    original_name: str
    file_type: str
    file_extension: str
    file_size: int
    file_path: str
    file_url: str
    thumbnail_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: str
    description: Optional[str] = None
    tags: list[str] = []
    width: Optional[int] = None
    height: Optional[int] = None
    upload_date: datetime
    uploaded_by: Optional[str] = None
    uploaded_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FileUpdateRequest(BaseModel):
    """Request schema for updating file metadata"""
    category: Optional[FileCategory] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None


class FilePaginatedResponse(BaseModel):
    """Response schema for paginated file listing"""
    files: list[FileListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
