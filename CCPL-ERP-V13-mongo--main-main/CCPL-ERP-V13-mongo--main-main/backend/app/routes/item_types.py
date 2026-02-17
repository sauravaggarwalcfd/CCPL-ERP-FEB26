"""
Item Types API Routes
CRUD operations for Item Type Master
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.item_type import (
    ItemType,
    ItemTypeCreate,
    ItemTypeUpdate,
    ItemTypeResponse,
    SEED_ITEM_TYPES,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def type_to_response(item_type: ItemType) -> ItemTypeResponse:
    return ItemTypeResponse(
        id=str(item_type.id),
        type_code=item_type.type_code,
        type_name=item_type.type_name,
        description=item_type.description,
        allow_purchase=item_type.allow_purchase,
        allow_sale=item_type.allow_sale,
        track_inventory=item_type.track_inventory,
        require_quality_check=item_type.require_quality_check,
        default_uom=item_type.default_uom,
        color_code=item_type.color_code,
        icon=item_type.icon,
        sort_order=item_type.sort_order,
        is_active=item_type.is_active,
        created_at=item_type.created_at,
        updated_at=item_type.updated_at,
    )


# ==================== LIST ====================

@router.get("", response_model=List[ItemTypeResponse])
async def list_item_types(
    is_active: Optional[bool] = Query(None),
    allow_purchase: Optional[bool] = Query(None),
    allow_sale: Optional[bool] = Query(None),
):
    """List all item types with optional filters"""
    
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    if allow_purchase is not None:
        query["allow_purchase"] = allow_purchase
    if allow_sale is not None:
        query["allow_sale"] = allow_sale
    
    types = await ItemType.find(query).sort("sort_order").to_list()
    return [type_to_response(t) for t in types]


# ==================== DROPDOWN ====================

@router.get("/dropdown")
async def get_item_types_dropdown(
    is_active: bool = True,
):
    """Get item types for dropdown selection"""
    
    types = await ItemType.find(
        ItemType.is_active == is_active
    ).sort("sort_order").to_list()
    
    return [
        {
            "value": t.type_code,
            "label": f"{t.type_code} - {t.type_name}",
            "name": t.type_name,
            "color": t.color_code,
            "icon": t.icon,
            "allow_purchase": t.allow_purchase,
            "allow_sale": t.allow_sale,
        }
        for t in types
    ]


# ==================== GET ONE ====================

@router.get("/{type_code}", response_model=ItemTypeResponse)
async def get_item_type(type_code: str):
    """Get a single item type by code"""
    
    item_type = await ItemType.find_one(
        ItemType.type_code == type_code.upper()
    )
    
    if not item_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item type '{type_code}' not found"
        )
    
    return type_to_response(item_type)


# ==================== CREATE ====================

@router.post("", response_model=ItemTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_item_type(data: ItemTypeCreate):
    """Create a new item type"""
    
    # Check if code exists
    existing = await ItemType.find_one(
        ItemType.type_code == data.type_code.upper()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item type with code '{data.type_code}' already exists"
        )
    
    item_type = ItemType(
        type_code=data.type_code.upper(),
        type_name=data.type_name,
        description=data.description,
        allow_purchase=data.allow_purchase,
        allow_sale=data.allow_sale,
        track_inventory=data.track_inventory,
        require_quality_check=data.require_quality_check,
        default_uom=data.default_uom,
        color_code=data.color_code,
        icon=data.icon,
        sort_order=data.sort_order,
    )
    
    await item_type.save()
    logger.info(f"Created item type: {item_type.type_code}")
    
    return type_to_response(item_type)


# ==================== UPDATE ====================

@router.put("/{type_code}", response_model=ItemTypeResponse)
async def update_item_type(type_code: str, data: ItemTypeUpdate):
    """Update an existing item type"""
    
    item_type = await ItemType.find_one(
        ItemType.type_code == type_code.upper()
    )
    
    if not item_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item type '{type_code}' not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(item_type, field, value)
    
    item_type.updated_at = datetime.utcnow()
    await item_type.save()
    
    logger.info(f"Updated item type: {item_type.type_code}")
    
    return type_to_response(item_type)


# ==================== DELETE ====================

@router.delete("/{type_code}")
async def delete_item_type(type_code: str):
    """Soft delete an item type"""
    
    item_type = await ItemType.find_one(
        ItemType.type_code == type_code.upper()
    )
    
    if not item_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item type '{type_code}' not found"
        )
    
    # TODO: Check if any items use this type before deleting
    
    item_type.is_active = False
    item_type.updated_at = datetime.utcnow()
    await item_type.save()
    
    logger.info(f"Deactivated item type: {item_type.type_code}")
    
    return {"message": f"Item type '{type_code}' deactivated", "type_code": type_code}


# ==================== SEED ====================

@router.post("/seed")
async def seed_item_types():
    """Seed default item types (run once)"""
    
    created = 0
    for data in SEED_ITEM_TYPES:
        existing = await ItemType.find_one(
            ItemType.type_code == data["type_code"]
        )
        if not existing:
            item_type = ItemType(**data)
            await item_type.save()
            created += 1
    
    return {"message": f"Seeded {created} item types", "total": len(SEED_ITEM_TYPES)}
