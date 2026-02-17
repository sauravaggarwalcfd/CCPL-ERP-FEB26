"""
Size Master API Routes
CRUD operations for Size Master with grouping
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.size_master import (
    SizeMaster,
    SizeCreate,
    SizeUpdate,
    SizeResponse
)
from ..models.variant_groups import VariantGroup, VariantType

router = APIRouter()
logger = logging.getLogger(__name__)


def size_to_response(size: SizeMaster) -> SizeResponse:
    """Convert SizeMaster document to response"""
    return SizeResponse(
        id=str(size.id),
        size_code=size.size_code,
        size_name=size.size_name,
        size_group=size.size_group,  # Now a string
        group_name=size.group_name,
        numeric_value=size.numeric_value,
        unit=size.unit,
        is_active=size.is_active,
        display_order=size.display_order,
        description=size.description,
        created_by=size.created_by,
        created_date=size.created_date,
        last_modified_by=size.last_modified_by,
        last_modified_date=size.last_modified_date,
    )


# ==================== LIST ====================

@router.get("/sizes", response_model=List[SizeResponse])
async def list_sizes(
    group: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List all sizes with optional filters"""
    query = {}

    if group:
        query["size_group"] = group

    if is_active is not None:
        query["is_active"] = is_active

    sizes = await SizeMaster.find(query).sort([
        ("size_group", 1),
        ("display_order", 1),
        ("size_name", 1)
    ]).to_list()

    return [size_to_response(s) for s in sizes]


# ==================== GET BY GROUP ====================

@router.get("/sizes/group/{group}", response_model=List[SizeResponse])
async def get_sizes_by_group(group: str):
    """Get sizes by group"""
    sizes = await SizeMaster.find(
        SizeMaster.size_group == group
    ).sort([
        ("display_order", 1),
        ("numeric_value", 1),
        ("size_name", 1)
    ]).to_list()

    return [size_to_response(s) for s in sizes]


# ==================== GET GROUPS ====================

@router.get("/sizes/groups")
async def get_size_groups():
    """Get all size groups from VariantGroup collection"""
    groups = await VariantGroup.find(
        VariantGroup.variant_type == VariantType.SIZE,
        VariantGroup.is_active == True
    ).sort("display_order", "group_name").to_list()
    
    return [
        {
            "code": group.group_code,
            "name": group.group_name,
            "value": group.group_code,
            "label": group.group_name
        }
        for group in groups
    ]


# ==================== GET ONE ====================

@router.get("/sizes/{code}", response_model=SizeResponse)
async def get_size(code: str):
    """Get a single size by code"""
    size = await SizeMaster.find_one(
        SizeMaster.size_code == code.upper()
    )

    if not size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Size '{code}' not found"
        )

    return size_to_response(size)


# ==================== CREATE ====================

@router.post("/sizes", response_model=SizeResponse, status_code=status.HTTP_201_CREATED)
async def create_size(data: SizeCreate):
    """Create a new size"""
    # Check if code exists
    existing = await SizeMaster.find_one(
        SizeMaster.size_code == data.size_code.upper()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Size with code '{data.size_code}' already exists"
        )

    # Validate group and get name
    group = await VariantGroup.find_one(
        VariantGroup.variant_type == VariantType.SIZE,
        VariantGroup.group_code == data.size_group
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid size group: '{data.size_group}'"
        )

    size = SizeMaster(
        size_code=data.size_code.upper(),
        size_name=data.size_name,
        size_group=data.size_group,
        group_name=group.group_name,
        numeric_value=data.numeric_value,
        unit=data.unit,
        display_order=data.display_order,
        description=data.description,
    )

    await size.save()
    logger.info(f"Created size: {size.size_code}")

    return size_to_response(size)


# ==================== UPDATE ====================

@router.put("/sizes/{code}", response_model=SizeResponse)
async def update_size(code: str, data: SizeUpdate):
    """Update an existing size"""
    size = await SizeMaster.find_one(
        SizeMaster.size_code == code.upper()
    )

    if not size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Size '{code}' not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    # Update group name if group changed
    if "size_group" in update_data:
        group = await VariantGroup.find_one(
            VariantGroup.variant_type == VariantType.SIZE,
            VariantGroup.group_code == update_data["size_group"]
        )
        if not group:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid size group: '{update_data['size_group']}'"
            )
        update_data["group_name"] = group.group_name

    for field, value in update_data.items():
        setattr(size, field, value)

    size.last_modified_date = datetime.utcnow()
    await size.save()

    logger.info(f"Updated size: {size.size_code}")

    return size_to_response(size)


# ==================== DELETE ====================

@router.delete("/sizes/{code}")
async def delete_size(code: str):
    """Soft delete a size (mark as inactive)"""
    size = await SizeMaster.find_one(
        SizeMaster.size_code == code.upper()
    )

    if not size:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Size '{code}' not found"
        )

    # TODO: Check if size is in use before deleting

    size.is_active = False
    size.last_modified_date = datetime.utcnow()
    await size.save()

    logger.info(f"Deactivated size: {size.size_code}")

    return {"message": f"Size '{code}' deactivated", "size_code": code}
