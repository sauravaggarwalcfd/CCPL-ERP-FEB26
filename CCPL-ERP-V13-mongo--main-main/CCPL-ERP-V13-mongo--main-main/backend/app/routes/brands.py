"""
Brand Master API Routes
CRUD operations for brand management
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.brand_master import (
    BrandMaster,
    BrandMasterCreate,
    BrandMasterUpdate,
    BrandMasterResponse
)
from ..core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_brand(
    data: BrandMasterCreate,
    current_user = Depends(get_current_user)
):
    """Create a new brand"""

    # Check if brand code already exists
    existing = await BrandMaster.find_one(
        BrandMaster.brand_code == data.brand_code,
        BrandMaster.deleted_at == None
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Brand with code '{data.brand_code}' already exists"
        )

    brand = await BrandMaster(
        **data.model_dump()
    ).insert()

    logger.info(f"Created Brand: {data.brand_code} - {data.brand_name}")

    return {
        "id": str(brand.id),
        "brand_code": brand.brand_code,
        "brand_name": brand.brand_name,
        "message": "Brand created successfully"
    }


@router.get("/", response_model=List[dict])
async def list_brands(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """List all brands with optional search and filtering"""

    query = {BrandMaster.deleted_at: None}

    if is_active is not None:
        query[BrandMaster.is_active] = is_active

    if search:
        query["$or"] = [
            {"brand_code": {"$regex": search, "$options": "i"}},
            {"brand_name": {"$regex": search, "$options": "i"}},
            {"brand_category": {"$regex": search, "$options": "i"}}
        ]

    brands = await BrandMaster.find(query).skip(skip).limit(limit).to_list()

    return [
        {
            "id": str(brand.id),
            "brand_code": brand.brand_code,
            "brand_name": brand.brand_name,
            "brand_category": brand.brand_category,
            "country": brand.country,
            "contact_person": brand.contact_person,
            "email": brand.email,
            "phone": brand.phone,
            "website": brand.website,
            "is_active": brand.is_active,
            "created_at": brand.created_at,
            "updated_at": brand.updated_at
        }
        for brand in brands
    ]


@router.get("/{brand_code}")
async def get_brand(
    brand_code: str,
    current_user = Depends(get_current_user)
):
    """Get a single brand by code"""

    brand = await BrandMaster.find_one(
        BrandMaster.brand_code == brand_code,
        BrandMaster.deleted_at == None
    )

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with code '{brand_code}' not found"
        )

    return {
        "id": str(brand.id),
        "brand_code": brand.brand_code,
        "brand_name": brand.brand_name,
        "brand_category": brand.brand_category,
        "country": brand.country,
        "contact_person": brand.contact_person,
        "email": brand.email,
        "phone": brand.phone,
        "website": brand.website,
        "is_active": brand.is_active,
        "created_at": brand.created_at,
        "updated_at": brand.updated_at
    }


@router.put("/{brand_code}")
async def update_brand(
    brand_code: str,
    data: BrandMasterUpdate,
    current_user = Depends(get_current_user)
):
    """Update a brand"""

    brand = await BrandMaster.find_one(
        BrandMaster.brand_code == brand_code,
        BrandMaster.deleted_at == None
    )

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with code '{brand_code}' not found"
        )

    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        for field, value in update_data.items():
            setattr(brand, field, value)
        await brand.save()

    logger.info(f"Updated Brand: {brand_code}")

    return {
        "id": str(brand.id),
        "brand_code": brand.brand_code,
        "brand_name": brand.brand_name,
        "message": "Brand updated successfully"
    }


@router.delete("/{brand_code}")
async def delete_brand(
    brand_code: str,
    current_user = Depends(get_current_user)
):
    """Soft delete a brand"""

    brand = await BrandMaster.find_one(
        BrandMaster.brand_code == brand_code,
        BrandMaster.deleted_at == None
    )

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with code '{brand_code}' not found"
        )

    brand.deleted_at = datetime.utcnow()
    brand.is_active = False
    await brand.save()

    logger.info(f"Deleted Brand: {brand_code}")

    return {
        "message": f"Brand '{brand_code}' deleted successfully"
    }


@router.get("/dropdown/list")
async def get_brands_dropdown(
    current_user = Depends(get_current_user)
):
    """Get brands for dropdown (active only)"""

    brands = await BrandMaster.find(
        BrandMaster.is_active == True,
        BrandMaster.deleted_at == None
    ).sort("+brand_name").to_list()

    return [
        {
            "value": brand.brand_code,
            "label": brand.brand_name
        }
        for brand in brands
    ]
