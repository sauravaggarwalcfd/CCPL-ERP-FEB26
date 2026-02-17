"""
UOM Master API Routes
CRUD operations for UOM Master with grouping and conversion
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.uom_master import (
    UOMMaster,
    UOMCreate,
    UOMUpdate,
    UOMResponse,
    convert_uom
)
from ..models.variant_groups import VariantGroup, VariantType

router = APIRouter()
logger = logging.getLogger(__name__)


def uom_to_response(uom: UOMMaster) -> UOMResponse:
    """Convert UOMMaster document to response"""
    return UOMResponse(
        id=str(uom.id),
        uom_code=uom.uom_code,
        uom_name=uom.uom_name,
        uom_group=uom.uom_group,  # Now a string
        group_name=uom.group_name,
        uom_symbol=uom.uom_symbol,
        conversion_to_base=uom.conversion_to_base,
        is_base_uom=uom.is_base_uom,
        is_active=uom.is_active,
        display_order=uom.display_order,
        description=uom.description,
        created_by=uom.created_by,
        created_date=uom.created_date,
        last_modified_by=uom.last_modified_by,
        last_modified_date=uom.last_modified_date,
    )


# ==================== LIST ====================

@router.get("/uoms", response_model=List[UOMResponse])
async def list_uoms(
    group: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List all UOMs with optional filters"""
    query = {}

    if group:
        query["uom_group"] = group

    if is_active is not None:
        query["is_active"] = is_active

    uoms = await UOMMaster.find(query).sort([
        ("uom_group", 1),
        ("display_order", 1),
        ("uom_name", 1)
    ]).to_list()

    return [uom_to_response(u) for u in uoms]


# ==================== GET BY GROUP ====================

@router.get("/uoms/group/{group}", response_model=List[UOMResponse])
async def get_uoms_by_group(group: str):
    """Get UOMs by group"""
    uoms = await UOMMaster.find(
        UOMMaster.uom_group == group
    ).sort([
        ("display_order", 1),
        ("uom_name", 1)
    ]).to_list()

    return [uom_to_response(u) for u in uoms]


# ==================== GET GROUPS ====================

@router.get("/uoms/groups")
async def get_uom_groups():
    """Get all UOM groups from VariantGroup collection"""
    groups = await VariantGroup.find(
        VariantGroup.variant_type == VariantType.UOM,
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

@router.get("/uoms/{code}", response_model=UOMResponse)
async def get_uom(code: str):
    """Get a single UOM by code"""
    uom = await UOMMaster.find_one(
        UOMMaster.uom_code == code.upper()
    )

    if not uom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UOM '{code}' not found"
        )

    return uom_to_response(uom)


# ==================== CREATE ====================

@router.post("/uoms", response_model=UOMResponse, status_code=status.HTTP_201_CREATED)
async def create_uom(data: UOMCreate):
    """Create a new UOM"""
    # Check if code exists
    existing = await UOMMaster.find_one(
        UOMMaster.uom_code == data.uom_code.upper()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"UOM with code '{data.uom_code}' already exists"
        )

    # Validate group and get name
    group = await VariantGroup.find_one(
        VariantGroup.variant_type == VariantType.UOM,
        VariantGroup.group_code == data.uom_group
    )
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UOM group: '{data.uom_group}'"
        )

    # If marked as base UOM, ensure no other base exists in this group
    if data.is_base_uom:
        existing_base = await UOMMaster.find_one(
            UOMMaster.uom_group == data.uom_group,
            UOMMaster.is_base_uom == True
        )
        if existing_base:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Base UOM already exists for group '{data.uom_group}': {existing_base.uom_code}"
            )

    uom = UOMMaster(
        uom_code=data.uom_code.upper(),
        uom_name=data.uom_name,
        uom_group=data.uom_group,
        group_name=group.group_name,
        uom_symbol=data.uom_symbol,
        conversion_to_base=data.conversion_to_base,
        is_base_uom=data.is_base_uom,
        display_order=data.display_order,
        description=data.description,
    )

    await uom.save()
    logger.info(f"Created UOM: {uom.uom_code}")

    return uom_to_response(uom)


# ==================== UPDATE ====================

@router.put("/uoms/{code}", response_model=UOMResponse)
async def update_uom(code: str, data: UOMUpdate):
    """Update an existing UOM"""
    uom = await UOMMaster.find_one(
        UOMMaster.uom_code == code.upper()
    )

    if not uom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UOM '{code}' not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    # If changing to base UOM, check no other base exists
    if "is_base_uom" in update_data and update_data["is_base_uom"]:
        existing_base = await UOMMaster.find_one(
            UOMMaster.uom_group == uom.uom_group,
            UOMMaster.is_base_uom == True,
            UOMMaster.uom_code != code.upper()
        )
        if existing_base:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Base UOM already exists for this group: {existing_base.uom_code}"
            )

    # Update group name if group changed
    if "uom_group" in update_data:
        group = await VariantGroup.find_one(
            VariantGroup.variant_type == VariantType.UOM,
            VariantGroup.group_code == update_data["uom_group"]
        )
        if not group:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UOM group: '{update_data['uom_group']}'"
            )
        update_data["group_name"] = group.group_name

    for field, value in update_data.items():
        setattr(uom, field, value)

    uom.last_modified_date = datetime.utcnow()
    await uom.save()

    logger.info(f"Updated UOM: {uom.uom_code}")

    return uom_to_response(uom)


# ==================== DELETE ====================

@router.delete("/uoms/{code}")
async def delete_uom(code: str):
    """Soft delete a UOM (mark as inactive)"""
    uom = await UOMMaster.find_one(
        UOMMaster.uom_code == code.upper()
    )

    if not uom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UOM '{code}' not found"
        )

    # Prevent deleting base UOM
    if uom.is_base_uom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete base UOM '{code}'. Set another UOM as base first."
        )

    # TODO: Check if UOM is in use before deleting

    uom.is_active = False
    uom.last_modified_date = datetime.utcnow()
    await uom.save()

    logger.info(f"Deactivated UOM: {uom.uom_code}")

    return {"message": f"UOM '{code}' deactivated", "uom_code": code}


# ==================== CONVERSION ====================

@router.get("/uoms/convert/{from_code}/{to_code}")
async def convert_value(
    from_code: str,
    to_code: str,
    value: float = Query(..., description="Value to convert")
):
    """Convert a value from one UOM to another"""
    from_uom = await UOMMaster.find_one(
        UOMMaster.uom_code == from_code.upper()
    )
    if not from_uom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source UOM '{from_code}' not found"
        )

    to_uom = await UOMMaster.find_one(
        UOMMaster.uom_code == to_code.upper()
    )
    if not to_uom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target UOM '{to_code}' not found"
        )

    try:
        converted_value = convert_uom(value, from_uom, to_uom)
        return {
            "from_uom": from_code.upper(),
            "to_uom": to_code.upper(),
            "from_value": value,
            "to_value": converted_value,
            "conversion_factor": to_uom.conversion_to_base / from_uom.conversion_to_base
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
