"""
Item Master API Routes
CRUD operations for items using the new 5-level hierarchy
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
import logging
from datetime import datetime, timedelta
from ..models.item import ItemMaster, ItemMasterCreate, ItemMasterUpdate, InventoryType
from ..models.category_hierarchy import ItemSubClass
from ..core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== ITEM MASTER ROUTES ====================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemMasterCreate,
    current_user = Depends(get_current_user)
):
    """Create a new Item Master entry"""

    # Check if non-deleted item already exists
    existing = await ItemMaster.find_one(
        ItemMaster.item_code == data.item_code,
        ItemMaster.deleted_at == None
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item with code '{data.item_code}' already exists"
        )
    
    # Build hierarchy path if sub_class_code provided
    hierarchy_path = None
    hierarchy_path_name = None
    
    if data.sub_class_code:
        sub_class = await ItemSubClass.find_one(ItemSubClass.sub_class_code == data.sub_class_code.upper())
        if sub_class:
            hierarchy_path = sub_class.path
            hierarchy_path_name = sub_class.path_name
    
    item = await ItemMaster(
        item_code=data.item_code,
        item_name=data.item_name,
        item_description=data.item_description,
        category_code=data.category_code,
        category_name=data.category_name,
        sub_category_code=data.sub_category_code,
        sub_category_name=data.sub_category_name,
        division_code=data.division_code,
        division_name=data.division_name,
        class_code=data.class_code,
        class_name=data.class_name,
        sub_class_code=data.sub_class_code,
        sub_class_name=data.sub_class_name,
        hierarchy_path=hierarchy_path,
        hierarchy_path_name=hierarchy_path_name,
        color_id=data.color_id,
        color_name=data.color_name,
        size_id=data.size_id,
        size_name=data.size_name,
        brand_id=data.brand_id,
        brand_name=data.brand_name,
        uom=data.uom,
        inventory_type=data.inventory_type,
        cost_price=data.cost_price,
        selling_price=data.selling_price,
        mrp=data.mrp,
        hsn_code=data.hsn_code,
        gst_rate=data.gst_rate,
        warehouse_id=data.warehouse_id,
        warehouse_name=data.warehouse_name,
        barcode=data.barcode,
        # File server fields (legacy)
        image_id=data.image_id,
        image_url=data.image_url,
        image_name=data.image_name,
        thumbnail_url=data.thumbnail_url,
        # BASE64 image fields (preferred)
        image_base64=data.image_base64,
        image_type=data.image_type,
        image_size=data.image_size,
        created_by=str(current_user.id) if current_user else None,
    ).insert()
    
    logger.info(f"Created Item: {data.item_code} - {data.item_name}")
    
    return {
        "id": str(item.id),
        "item_code": item.item_code,
        "item_name": item.item_name,
        "message": "Item created successfully"
    }


@router.get("/", response_model=List[dict])
async def list_items(
    category_code: Optional[str] = Query(None),
    sub_category_code: Optional[str] = Query(None),
    division_code: Optional[str] = Query(None),
    class_code: Optional[str] = Query(None),
    sub_class_code: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user = Depends(get_current_user)
):
    """List all items with optional filters"""
    
    query_conditions = []
    
    # Exclude deleted items from main list
    query_conditions.append(ItemMaster.deleted_at == None)
    
    if category_code:
        query_conditions.append(ItemMaster.category_code == category_code.upper())
    if sub_category_code:
        query_conditions.append(ItemMaster.sub_category_code == sub_category_code.upper())
    if division_code:
        query_conditions.append(ItemMaster.division_code == division_code.upper())
    if class_code:
        query_conditions.append(ItemMaster.class_code == class_code.upper())
    if sub_class_code:
        query_conditions.append(ItemMaster.sub_class_code == sub_class_code.upper())
    if is_active is not None:
        query_conditions.append(ItemMaster.is_active == is_active)
    
    if query_conditions:
        items = await ItemMaster.find(*query_conditions).skip(skip).limit(limit).to_list()
    else:
        items = await ItemMaster.find_all().skip(skip).limit(limit).to_list()
    
    # Apply search filter in memory if provided
    if search:
        search_lower = search.lower()
        items = [
            i for i in items
            if search_lower in i.item_name.lower() or 
               search_lower in i.item_code.lower() or
               (i.barcode and search_lower in i.barcode.lower())
        ]
    
    return [
        {
            "id": str(i.id),
            "item_code": i.item_code,
            "item_name": i.item_name,
            "item_description": i.item_description,
            "category_code": i.category_code,
            "category_name": i.category_name,
            "sub_category_code": i.sub_category_code,
            "sub_category_name": i.sub_category_name,
            "division_code": i.division_code,
            "division_name": i.division_name,
            "class_code": i.class_code,
            "class_name": i.class_name,
            "sub_class_code": i.sub_class_code,
            "sub_class_name": i.sub_class_name,
            "hierarchy_path": i.hierarchy_path,
            "hierarchy_path_name": i.hierarchy_path_name,
            "uom": i.uom,
            "cost_price": i.cost_price,
            "selling_price": i.selling_price,
            "mrp": i.mrp,
            "current_stock": i.current_stock,
            "image_id": i.image_id,
            "image_url": i.image_url,
            "image_name": i.image_name,
            "thumbnail_url": i.thumbnail_url,
            "is_active": i.is_active,
        }
        for i in items
    ]


@router.get("/{item_code}")
async def get_item(
    item_code: str,
    current_user = Depends(get_current_user)
):
    """Get a specific item by code"""
    
    item = await ItemMaster.find_one(ItemMaster.item_code == item_code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_code}' not found"
        )
    
    return {
        "id": str(item.id),
        "item_code": item.item_code,
        "item_name": item.item_name,
        "item_description": item.item_description,
        "category_code": item.category_code,
        "category_name": item.category_name,
        "sub_category_code": item.sub_category_code,
        "sub_category_name": item.sub_category_name,
        "division_code": item.division_code,
        "division_name": item.division_name,
        "class_code": item.class_code,
        "class_name": item.class_name,
        "sub_class_code": item.sub_class_code,
        "sub_class_name": item.sub_class_name,
        "hierarchy_path": item.hierarchy_path,
        "hierarchy_path_name": item.hierarchy_path_name,
        "color_id": item.color_id,
        "color_name": item.color_name,
        "size_id": item.size_id,
        "size_name": item.size_name,
        "brand_id": item.brand_id,
        "brand_name": item.brand_name,
        "uom": item.uom,
        "inventory_type": item.inventory_type,
        "cost_price": item.cost_price,
        "selling_price": item.selling_price,
        "mrp": item.mrp,
        "hsn_code": item.hsn_code,
        "gst_rate": item.gst_rate,
        "warehouse_id": item.warehouse_id,
        "warehouse_name": item.warehouse_name,
        "bin_location": item.bin_location,
        "min_stock_level": item.min_stock_level,
        "max_stock_level": item.max_stock_level,
        "reorder_point": item.reorder_point,
        "reorder_quantity": item.reorder_quantity,
        "current_stock": item.current_stock,
        "barcode": item.barcode,
        "serial_tracked": item.serial_tracked,
        "batch_tracked": item.batch_tracked,
        "image_id": item.image_id,
        "image_url": item.image_url,
        "image_name": item.image_name,
        "thumbnail_url": item.thumbnail_url,
        "is_active": item.is_active,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


@router.put("/{item_code}")
async def update_item(
    item_code: str,
    data: ItemMasterUpdate,
    current_user = Depends(get_current_user)
):
    """Update an item"""
    
    item = await ItemMaster.find_one(ItemMaster.item_code == item_code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_code}' not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    item.updated_at = datetime.utcnow()
    item.updated_by = str(current_user.id) if current_user else None
    await item.save()
    
    return {"message": "Item updated successfully", "item_code": item_code}


@router.get("/next-sku/{prefix}")
async def get_next_sku(prefix: str):
    """Get next available SKU for given prefix (item type code)"""
    try:
        # Normalize prefix to 2 uppercase letters
        prefix = prefix[:2].upper()

        # Find all NON-DELETED items with this prefix
        items = await ItemMaster.find(
            {
                "item_code": {"$regex": f"^{prefix}\\d{{5}}$"},
                "deleted_at": None  # Exclude deleted items
            }
        ).to_list()

        if not items:
            # No items with this prefix yet, start from 1
            return {"next_sku": f"{prefix}00001", "sequence": 1}

        # Extract numeric parts and find the maximum
        max_sequence = 0
        for item in items:
            try:
                numeric_part = int(item.item_code[2:])
                if numeric_part > max_sequence:
                    max_sequence = numeric_part
            except (ValueError, IndexError):
                continue

        # Generate next SKU
        next_sequence = max_sequence + 1
        next_sku = f"{prefix}{str(next_sequence).zfill(5)}"

        return {"next_sku": next_sku, "sequence": next_sequence}
    except Exception as e:
        logger.error(f"Error generating next SKU: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate next SKU: {str(e)}"
        )


@router.delete("/{item_code}")
async def delete_item(
    item_code: str,
    current_user = Depends(get_current_user)
):
    """Soft delete an item (move to bin)"""
    
    item = await ItemMaster.find_one(ItemMaster.item_code == item_code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_code}' not found"
        )
    
    if item.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item '{item_code}' is already in bin"
        )
    
    item.deleted_at = datetime.utcnow()
    item.deleted_by = str(current_user.id) if current_user else None
    item.is_active = False
    item.updated_at = datetime.utcnow()
    item.updated_by = str(current_user.id) if current_user else None
    await item.save()
    
    return {"message": "Item moved to bin successfully", "item_code": item_code}


# ==================== BIN MANAGEMENT ROUTES ====================

@router.get("/bin/list")
async def list_bin_items(
    current_user = Depends(get_current_user)
):
    """List all items in bin (deleted items)"""
    
    # Find all deleted items
    items = await ItemMaster.find(ItemMaster.deleted_at != None).to_list()
    
    # Calculate days in bin and filter items older than 10 days
    now = datetime.utcnow()
    result = []
    
    for item in items:
        if item.deleted_at:
            days_in_bin = (now - item.deleted_at).days
            
            result.append({
                "id": str(item.id),
                "item_code": item.item_code,
                "item_name": item.item_name,
                "category_name": item.category_name,
                "sub_category_name": item.sub_category_name,
                "deleted_at": item.deleted_at.isoformat(),
                "deleted_by": item.deleted_by,
                "days_in_bin": days_in_bin,
                "can_restore": days_in_bin <= 10
            })
    
    return result


@router.post("/bin/restore/{item_code}")
async def restore_item(
    item_code: str,
    current_user = Depends(get_current_user)
):
    """Restore an item from bin"""
    
    item = await ItemMaster.find_one(ItemMaster.item_code == item_code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_code}' not found"
        )
    
    if not item.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item '{item_code}' is not in bin"
        )
    
    # Check if within 10 days
    days_in_bin = (datetime.utcnow() - item.deleted_at).days
    if days_in_bin > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot restore item after 10 days (currently {days_in_bin} days in bin)"
        )
    
    # Restore the item
    item.deleted_at = None
    item.deleted_by = None
    item.is_active = True
    item.updated_at = datetime.utcnow()
    item.updated_by = str(current_user.id) if current_user else None
    await item.save()
    
    return {"message": "Item restored successfully", "item_code": item_code}


@router.delete("/bin/permanent/{item_code}")
async def permanent_delete_item(
    item_code: str,
    current_user = Depends(get_current_user)
):
    """Permanently delete an item from bin"""
    
    item = await ItemMaster.find_one(ItemMaster.item_code == item_code)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item '{item_code}' not found"
        )
    
    if not item.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item '{item_code}' is not in bin. Move to bin first before permanent deletion."
        )
    
    # Store item code for response
    deleted_code = item.item_code
    
    # Permanently delete from database
    await item.delete()
    
    return {
        "message": "Item permanently deleted", 
        "item_code": deleted_code,
        "note": "SKU is now available for reuse"
    }


@router.post("/bin/cleanup")
async def cleanup_old_bin_items(
    current_user = Depends(get_current_user)
):
    """Automatically delete items in bin older than 10 days"""
    
    # Find all deleted items older than 10 days
    ten_days_ago = datetime.utcnow() - timedelta(days=10)
    old_items = await ItemMaster.find(
        ItemMaster.deleted_at != None,
        ItemMaster.deleted_at < ten_days_ago
    ).to_list()
    
    deleted_count = 0
    deleted_codes = []
    
    for item in old_items:
        deleted_codes.append(item.item_code)
        await item.delete()
        deleted_count += 1
    
    return {
        "message": f"Cleaned up {deleted_count} items from bin",
        "deleted_codes": deleted_codes
    }
