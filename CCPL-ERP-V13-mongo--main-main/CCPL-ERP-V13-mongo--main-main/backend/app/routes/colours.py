"""
Colour Master API Routes
CRUD operations for Colour Master with grouping
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.colour_master import (
    ColourMaster,
    ColourCreate,
    ColourUpdate,
    ColourResponse,
    hex_to_rgb
)
from ..models.variant_groups import VariantGroup, VariantType

router = APIRouter()
logger = logging.getLogger(__name__)


def colour_to_response(colour: ColourMaster) -> ColourResponse:
    """Convert ColourMaster document to response"""
    return ColourResponse(
        id=str(colour.id),
        colour_code=colour.colour_code,
        colour_name=colour.colour_name,
        colour_hex=colour.colour_hex,
        rgb_value=colour.rgb_value,
        colour_group=colour.colour_group,  # Now a string
        group_name=colour.group_name,
        is_active=colour.is_active,
        display_order=colour.display_order,
        description=colour.description,
        created_by=colour.created_by,
        created_date=colour.created_date,
        last_modified_by=colour.last_modified_by,
        last_modified_date=colour.last_modified_date,
    )


# ==================== LIST ====================

@router.get("/colours", response_model=List[ColourResponse])
async def list_colours(
    group: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List all colours with optional filters"""
    query = {}

    if group:
        query["colour_group"] = group

    if is_active is not None:
        query["is_active"] = is_active

    colours = await ColourMaster.find(query).sort([
        ("colour_group", 1),
        ("display_order", 1),
        ("colour_name", 1)
    ]).to_list()

    return [colour_to_response(c) for c in colours]


# ==================== GET BY GROUP ====================

@router.get("/colours/group/{group}", response_model=List[ColourResponse])
async def get_colours_by_group(group: str):
    """Get colours by group"""
    colours = await ColourMaster.find(
        ColourMaster.colour_group == group
    ).sort([
        ("display_order", 1),
        ("colour_name", 1)
    ]).to_list()

    return [colour_to_response(c) for c in colours]


# ==================== GET GROUPS ====================

@router.get("/colours/groups")
async def get_colour_groups():
    """Get all colour groups from VariantGroup collection"""
    groups = await VariantGroup.find(
        VariantGroup.variant_type == VariantType.COLOUR,
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

@router.get("/colours/{code}", response_model=ColourResponse)
async def get_colour(code: str):
    """Get a single colour by code"""
    colour = await ColourMaster.find_one(
        ColourMaster.colour_code == code.upper()
    )

    if not colour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Colour '{code}' not found"
        )

    return colour_to_response(colour)


# ==================== CREATE ====================

@router.post("/colours", response_model=ColourResponse, status_code=status.HTTP_201_CREATED)
async def create_colour(data: ColourCreate):
    """Create a new colour"""
    # Check if code exists
    existing = await ColourMaster.find_one(
        ColourMaster.colour_code == data.colour_code.upper()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Colour with code '{data.colour_code}' already exists"
        )

    # Validate group and get name
    group = await VariantGroup.find_one(
        VariantGroup.variant_type == VariantType.COLOUR,
        VariantGroup.group_code == data.colour_group
    )
    
    if not group:
        # Fallback for migration/legacy support or auto-create?
        # For now, strict validation is better to ensure consistency
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid colour group: '{data.colour_group}'"
        )

    # Convert hex to RGB
    rgb = hex_to_rgb(data.colour_hex)

    colour = ColourMaster(
        colour_code=data.colour_code.upper(),
        colour_name=data.colour_name,
        colour_hex=data.colour_hex.upper(),
        rgb_value=rgb,
        colour_group=data.colour_group,
        group_name=group.group_name,
        display_order=data.display_order,
        description=data.description,
    )

    await colour.save()
    logger.info(f"Created colour: {colour.colour_code}")

    return colour_to_response(colour)


# ==================== UPDATE ====================

@router.put("/colours/{code}", response_model=ColourResponse)
async def update_colour(code: str, data: ColourUpdate):
    """Update an existing colour"""
    colour = await ColourMaster.find_one(
        ColourMaster.colour_code == code.upper()
    )

    if not colour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Colour '{code}' not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    # Update hex and RGB if hex changed
    if "colour_hex" in update_data:
        update_data["rgb_value"] = hex_to_rgb(update_data["colour_hex"])

    # Update group name if group changed
    if "colour_group" in update_data:
        group = await VariantGroup.find_one(
            VariantGroup.variant_type == VariantType.COLOUR,
            VariantGroup.group_code == update_data["colour_group"]
        )
        if not group:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid colour group: '{update_data['colour_group']}'"
            )
        update_data["group_name"] = group.group_name

    for field, value in update_data.items():
        setattr(colour, field, value)

    colour.last_modified_date = datetime.utcnow()
    await colour.save()

    logger.info(f"Updated colour: {colour.colour_code}")

    return colour_to_response(colour)


# ==================== DELETE ====================

@router.delete("/colours/{code}")
async def delete_colour(code: str):
    """Soft delete a colour (mark as inactive)"""
    colour = await ColourMaster.find_one(
        ColourMaster.colour_code == code.upper()
    )

    if not colour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Colour '{code}' not found"
        )

    # TODO: Check if colour is in use before deleting

    colour.is_active = False
    colour.last_modified_date = datetime.utcnow()
    await colour.save()

    logger.info(f"Deactivated colour: {colour.colour_code}")

    return {"message": f"Colour '{code}' deactivated", "colour_code": code}


# ==================== HEX PREVIEW ====================

@router.get("/colours/hex-preview/{hex}")
async def hex_preview(hex: str):
    """Preview a hex colour"""
    try:
        if not hex.startswith('#'):
            hex = '#' + hex
        rgb = hex_to_rgb(hex)
        return {
            "hex": hex.upper(),
            "rgb": rgb.model_dump(),
            "valid": True
        }
    except Exception as e:
        return {
            "hex": hex,
            "error": str(e),
            "valid": False
        }
