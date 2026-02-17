"""
Variant Groups API Routes
CRUD operations for Variant Group definitions
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.variant_groups import (
    VariantGroup,
    VariantGroupResponse,
    VariantType,
    VariantGroupCreate,
    VariantGroupUpdate
)

router = APIRouter()
logger = logging.getLogger(__name__)


def group_to_response(group: VariantGroup) -> VariantGroupResponse:
    """Convert VariantGroup document to response"""
    return VariantGroupResponse(
        id=str(group.id),
        variant_type=group.variant_type,
        group_code=group.group_code,
        group_name=group.group_name,
        description=group.description,
        is_active=group.is_active,
        display_order=group.display_order,
        created_date=group.created_date,
    )


# ==================== LIST ====================

@router.get("/variant-groups", response_model=List[VariantGroupResponse])
async def list_variant_groups(
    variant_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List all variant groups with optional filters"""
    query = {}

    if variant_type:
        query["variant_type"] = variant_type

    if is_active is not None:
        query["is_active"] = is_active

    groups = await VariantGroup.find(query).sort([
        ("variant_type", 1),
        ("display_order", 1),
        ("group_name", 1)
    ]).to_list()

    return [group_to_response(g) for g in groups]


# ==================== GET BY TYPE ====================

@router.get("/variant-groups/type/{variant_type}", response_model=List[VariantGroupResponse])
async def get_groups_by_type(variant_type: str):
    """Get variant groups by type (COLOUR, SIZE, UOM)"""
    groups = await VariantGroup.find(
        VariantGroup.variant_type == variant_type.upper()
    ).sort([
        ("display_order", 1),
        ("group_name", 1)
    ]).to_list()

    return [group_to_response(g) for g in groups]


# ==================== GET TYPES ====================

@router.get("/variant-groups/types")
async def get_variant_types():
    """Get all variant types"""
    return [
        {
            "code": vtype.value,
            "name": vtype.value.title(),
            "value": vtype.value,
            "label": vtype.value.title()
        }
        for vtype in VariantType
    ]


# ==================== GET ONE ====================

@router.get("/variant-groups/{group_code}", response_model=VariantGroupResponse)
async def get_variant_group(group_code: str):
    """Get a single variant group by code"""
    group = await VariantGroup.find_one(
        VariantGroup.group_code == group_code.upper()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant group '{group_code}' not found"
        )

    return group_to_response(group)


# ==================== SUMMARY ====================

@router.get("/variant-groups/summary/all")
async def get_variant_groups_summary():
    """Get summary of all variant groups organized by type"""
    summary = {}

    for vtype in VariantType:
        groups = await VariantGroup.find(
            VariantGroup.variant_type == vtype.value,
            VariantGroup.is_active == True
        ).sort([
            ("display_order", 1),
            ("group_name", 1)
        ]).to_list()

        summary[vtype.value] = [
            {
                "code": g.group_code,
                "name": g.group_name,
                "description": g.description
            }
            for g in groups
        ]

    return summary


# ==================== CREATE ====================

@router.post("/variant-groups", response_model=VariantGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_variant_group(group_in: VariantGroupCreate):
    """Create a new variant group"""
    # Check if group code already exists
    existing_group = await VariantGroup.find_one(
        VariantGroup.group_code == group_in.group_code.upper()
    )
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Variant group with code '{group_in.group_code}' already exists"
        )

    group = VariantGroup(
        variant_type=group_in.variant_type,
        group_code=group_in.group_code.upper(),
        group_name=group_in.group_name,
        description=group_in.description,
        is_active=group_in.is_active,
        display_order=group_in.display_order,
        created_date=datetime.utcnow()
    )
    await group.insert()
    return group_to_response(group)


# ==================== UPDATE ====================

@router.put("/variant-groups/{group_code}", response_model=VariantGroupResponse)
async def update_variant_group(group_code: str, group_in: VariantGroupUpdate):
    """Update a variant group"""
    group = await VariantGroup.find_one(
        VariantGroup.group_code == group_code.upper()
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant group '{group_code}' not found"
        )

    if group_in.group_name is not None:
        group.group_name = group_in.group_name
    if group_in.description is not None:
        group.description = group_in.description
    if group_in.is_active is not None:
        group.is_active = group_in.is_active
    if group_in.display_order is not None:
        group.display_order = group_in.display_order

    await group.save()
    return group_to_response(group)


# ==================== DELETE ====================

@router.delete("/variant-groups/{group_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant_group(group_code: str):
    """Delete a variant group"""
    group = await VariantGroup.find_one(
        VariantGroup.group_code == group_code.upper()
    )
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant group '{group_code}' not found"
        )

    await group.delete()
    return None
