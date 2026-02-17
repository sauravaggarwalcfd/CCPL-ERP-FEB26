"""
Category Hierarchy API Routes - FIXED VERSION
CRUD operations for 5-level category hierarchy
Uses insert() instead of save() to avoid Beanie initialization issues
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from ..models.category_hierarchy import (
    ItemCategory, ItemSubCategory, ItemDivision, ItemClass, ItemSubClass,
    ItemCategoryCreate, ItemSubCategoryCreate, ItemDivisionCreate, ItemClassCreate, ItemSubClassCreate,
    ItemCategoryUpdate, ItemSubCategoryUpdate, ItemDivisionUpdate, ItemClassUpdate, ItemSubClassUpdate,
    SEED_CATEGORIES, SEED_SUB_CATEGORIES, SEED_DIVISIONS, SEED_CLASSES, SEED_SUB_CLASSES,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== HELPER FUNCTIONS ====================

def build_path(codes: List[str]) -> str:
    return "/".join(codes)

def build_path_name(names: List[str]) -> str:
    return " > ".join(names)


# ==================== LEVEL 1: CATEGORIES ====================

@router.get("/categories", response_model=List[dict])
async def list_categories(
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
):
    """List all Level 1 categories"""
    
    if is_active is not None:
        categories = await ItemCategory.find(
            ItemCategory.is_active == is_active
        ).sort("sort_order").to_list()
    else:
        categories = await ItemCategory.find_all().sort("sort_order").to_list()
    
    if search:
        search_lower = search.lower()
        categories = [c for c in categories if search_lower in c.category_name.lower() or search_lower in c.category_code.lower()]
    
    return [
        {
            "id": str(c.id),
            "level": 1,
            "code": c.category_code,
            "name": c.category_name,
            "description": c.description,
            "path": c.category_code,
            "path_name": c.category_name,
            "item_type": c.item_type,
            "level_names": c.level_names,
            "has_color": c.has_color,
            "has_size": c.has_size,
            "has_fabric": c.has_fabric,
            "default_hsn_code": c.default_hsn_code,
            "default_gst_rate": c.default_gst_rate,
            "icon": c.icon,
            "color_code": c.color_code,
            "sort_order": c.sort_order,
            "is_active": c.is_active,
            "child_count": c.child_count,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in categories
    ]


@router.get("/categories/{code}")
async def get_category(code: str):
    """Get a single category by code"""
    
    category = await ItemCategory.find_one(ItemCategory.category_code == code.upper())
    
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{code}' not found")
    
    return {
        "id": str(category.id),
        "level": 1,
        "code": category.category_code,
        "name": category.category_name,
        "description": category.description,
        "path": category.category_code,
        "path_name": category.category_name,
        "item_type": category.item_type,
        "level_names": category.level_names,
        "has_color": category.has_color,
        "has_size": category.has_size,
        "has_fabric": category.has_fabric,
        "has_brand": category.has_brand,
        "has_style": category.has_style,
        "has_season": category.has_season,
        "default_hsn_code": category.default_hsn_code,
        "default_gst_rate": category.default_gst_rate,
        "default_uom": category.default_uom,
        "icon": category.icon,
        "color_code": category.color_code,
        "sort_order": category.sort_order,
        "is_active": category.is_active,
        "child_count": category.child_count,
    }


@router.post("/categories", status_code=201)
async def create_category(data: ItemCategoryCreate):
    """Create a new Level 1 category"""
    
    existing = await ItemCategory.find_one(ItemCategory.category_code == data.category_code.upper())
    if existing:
        raise HTTPException(status_code=400, detail=f"Category '{data.category_code}' already exists")
    
    # Use insert() instead of save()
    category = await ItemCategory(
        category_code=data.category_code.upper(),
        category_name=data.category_name,
        description=data.description,
        item_type=data.item_type.upper(),
        level_names=data.level_names,
        has_color=data.has_color,
        has_size=data.has_size,
        has_fabric=data.has_fabric,
        has_brand=data.has_brand,
        has_style=data.has_style,
        has_season=data.has_season,
        default_hsn_code=data.default_hsn_code,
        default_gst_rate=data.default_gst_rate,
        default_uom=data.default_uom,
        icon=data.icon,
        color_code=data.color_code,
        sort_order=data.sort_order,
    ).insert()
    
    logger.info(f"Created category: {category.category_code}")
    
    return {"message": "Category created", "code": category.category_code}


@router.put("/categories/{code}")
async def update_category(code: str, data: ItemCategoryUpdate):
    """Update a category"""
    
    category = await ItemCategory.find_one(ItemCategory.category_code == code.upper())
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{code}' not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    category.updated_at = datetime.utcnow()
    await category.save()
    
    return {"message": "Category updated", "code": category.category_code}


@router.delete("/categories/{code}")
async def delete_category(code: str, force: bool = Query(False, description="Force delete with all children")):
    """Soft delete a category with optional cascade deletion"""
    
    category = await ItemCategory.find_one(ItemCategory.category_code == code.upper())
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{code}' not found")
    
    # Check for children (exclude already deleted items)
    children = await ItemSubCategory.find(
        ItemSubCategory.category_code == code.upper(),
        ItemSubCategory.is_deleted == False
    ).count()
    if children > 0 and not force:
        raise HTTPException(status_code=400, detail=f"Cannot delete: {children} sub-categories exist. Use force=true to delete all children.")
    
    # If force=true, cascade delete all children
    if force and children > 0:
        await cascade_delete_category_children(code.upper())
    
    # Move to bin (soft delete)
    category.is_active = False
    category.is_deleted = True
    category.deleted_at = datetime.utcnow()
    category.updated_at = datetime.utcnow()
    await category.save()

    return {"message": "Category moved to bin", "code": code, "children_deleted": children if force else 0}


# ==================== LEVEL 2: SUB-CATEGORIES ====================

@router.get("/sub-categories", response_model=List[dict])
async def list_sub_categories(
    category_code: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List Level 2 sub-categories, optionally filtered by parent"""
    
    query_conditions = []
    
    if category_code:
        query_conditions.append(ItemSubCategory.category_code == category_code.upper())
    if is_active is not None:
        query_conditions.append(ItemSubCategory.is_active == is_active)
    
    if query_conditions:
        items = await ItemSubCategory.find(*query_conditions).sort("sort_order").to_list()
    else:
        items = await ItemSubCategory.find_all().sort("sort_order").to_list()
    
    return [
        {
            "id": str(i.id),
            "level": 2,
            "code": i.sub_category_code,
            "name": i.sub_category_name,
            "description": i.description,
            "category_code": i.category_code,
            "category_name": i.category_name,
            "path": i.path,
            "path_name": i.path_name,
            "icon": i.icon,
            "color_code": i.color_code,
            "sort_order": i.sort_order,
            "is_active": i.is_active,
            "child_count": i.child_count,
        }
        for i in items
    ]


@router.post("/sub-categories", status_code=201)
async def create_sub_category(data: ItemSubCategoryCreate):
    """Create a new Level 2 sub-category"""
    
    # Validate parent
    parent = await ItemCategory.find_one(ItemCategory.category_code == data.category_code.upper())
    if not parent:
        raise HTTPException(status_code=400, detail=f"Parent category '{data.category_code}' not found")
    
    # Check unique
    existing = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data.sub_category_code.upper())
    if existing:
        raise HTTPException(status_code=400, detail=f"Sub-category '{data.sub_category_code}' already exists")
    
    # Use insert() instead of save()
    item = await ItemSubCategory(
        sub_category_code=data.sub_category_code.upper(),
        sub_category_name=data.sub_category_name,
        description=data.description,
        category_code=parent.category_code,
        category_name=parent.category_name,
        path=build_path([parent.category_code, data.sub_category_code.upper()]),
        path_name=build_path_name([parent.category_name, data.sub_category_name]),
        has_color=data.has_color,
        has_size=data.has_size,
        has_fabric=data.has_fabric,
        icon=data.icon,
        color_code=data.color_code,
        sort_order=data.sort_order,
    ).insert()
    
    # Update parent count (exclude deleted items)
    parent.child_count = await ItemSubCategory.find(
        ItemSubCategory.category_code == parent.category_code,
        ItemSubCategory.is_deleted == False
    ).count()
    await parent.save()
    
    return {"message": "Sub-category created", "code": item.sub_category_code}


@router.put("/sub-categories/{code}")
async def update_sub_category(code: str, data: ItemSubCategoryUpdate):
    """Update a sub-category"""
    
    item = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Sub-category '{code}' not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    # Update path_name if name changed
    if data.sub_category_name:
        item.path_name = build_path_name([item.category_name, data.sub_category_name])
    
    item.updated_at = datetime.utcnow()
    await item.save()
    
    return {"message": "Sub-category updated", "code": item.sub_category_code}


@router.delete("/sub-categories/{code}")
async def delete_sub_category(code: str, force: bool = Query(False, description="Force delete with all children")):
    """Soft delete a sub-category with optional cascade deletion"""
    
    item = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Sub-category '{code}' not found")
    
    children = await ItemDivision.find(
        ItemDivision.sub_category_code == code.upper(),
        ItemDivision.is_deleted == False
    ).count()
    if children > 0 and not force:
        raise HTTPException(status_code=400, detail=f"Cannot delete: {children} divisions exist. Use force=true to delete all children.")
    
    # If force=true, cascade delete all children
    if force and children > 0:
        await cascade_delete_sub_category_children(code.upper())
    
    # Move to bin (soft delete)
    item.is_active = False
    item.is_deleted = True
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    await item.save()

    # Update parent's child count
    parent = await ItemCategory.find_one(ItemCategory.category_code == item.category_code)
    if parent:
        parent.child_count = await ItemSubCategory.find(
            ItemSubCategory.category_code == parent.category_code,
            ItemSubCategory.is_deleted == False
        ).count()
        await parent.save()

    return {"message": "Sub-category moved to bin", "code": code, "children_deleted": children if force else 0}


# ==================== LEVEL 3: DIVISIONS ====================

@router.get("/divisions", response_model=List[dict])
async def list_divisions(
    category_code: Optional[str] = Query(None),
    sub_category_code: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List Level 3 divisions"""
    
    query_conditions = []
    
    if category_code:
        query_conditions.append(ItemDivision.category_code == category_code.upper())
    if sub_category_code:
        query_conditions.append(ItemDivision.sub_category_code == sub_category_code.upper())
    if is_active is not None:
        query_conditions.append(ItemDivision.is_active == is_active)
    
    if query_conditions:
        items = await ItemDivision.find(*query_conditions).sort("sort_order").to_list()
    else:
        items = await ItemDivision.find_all().sort("sort_order").to_list()
    
    return [
        {
            "id": str(i.id),
            "level": 3,
            "code": i.division_code,
            "name": i.division_name,
            "description": i.description,
            "category_code": i.category_code,
            "category_name": i.category_name,
            "sub_category_code": i.sub_category_code,
            "sub_category_name": i.sub_category_name,
            "path": i.path,
            "path_name": i.path_name,
            "icon": i.icon,
            "color_code": i.color_code,
            "sort_order": i.sort_order,
            "is_active": i.is_active,
            "child_count": i.child_count,
        }
        for i in items
    ]


@router.post("/divisions", status_code=201)
async def create_division(data: ItemDivisionCreate):
    """Create a new Level 3 division"""
    
    # Validate parents
    cat = await ItemCategory.find_one(ItemCategory.category_code == data.category_code.upper())
    if not cat:
        raise HTTPException(status_code=400, detail=f"Category '{data.category_code}' not found")
    
    subcat = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data.sub_category_code.upper())
    if not subcat:
        raise HTTPException(status_code=400, detail=f"Sub-category '{data.sub_category_code}' not found")
    
    existing = await ItemDivision.find_one(ItemDivision.division_code == data.division_code.upper())
    if existing:
        raise HTTPException(status_code=400, detail=f"Division '{data.division_code}' already exists")
    
    # Use insert() instead of save()
    item = await ItemDivision(
        division_code=data.division_code.upper(),
        division_name=data.division_name,
        description=data.description,
        category_code=cat.category_code,
        category_name=cat.category_name,
        sub_category_code=subcat.sub_category_code,
        sub_category_name=subcat.sub_category_name,
        path=build_path([cat.category_code, subcat.sub_category_code, data.division_code.upper()]),
        path_name=build_path_name([cat.category_name, subcat.sub_category_name, data.division_name]),
        has_color=data.has_color,
        has_size=data.has_size,
        has_fabric=data.has_fabric,
        icon=data.icon,
        color_code=data.color_code,
        sort_order=data.sort_order,
    ).insert()
    
    subcat.child_count = await ItemDivision.find(
        ItemDivision.sub_category_code == subcat.sub_category_code,
        ItemDivision.is_deleted == False
    ).count()
    await subcat.save()
    
    return {"message": "Division created", "code": item.division_code}


@router.put("/divisions/{code}")
async def update_division(code: str, data: ItemDivisionUpdate):
    item = await ItemDivision.find_one(ItemDivision.division_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Division '{code}' not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    if data.division_name:
        item.path_name = build_path_name([item.category_name, item.sub_category_name, data.division_name])
    
    item.updated_at = datetime.utcnow()
    await item.save()
    
    return {"message": "Division updated", "code": item.division_code}


@router.delete("/divisions/{code}")
async def delete_division(code: str, force: bool = Query(False, description="Force delete with all children")):
    """Soft delete a division with optional cascade deletion"""
    
    item = await ItemDivision.find_one(ItemDivision.division_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Division '{code}' not found")
    
    children = await ItemClass.find(
        ItemClass.division_code == code.upper(),
        ItemClass.is_deleted == False
    ).count()
    if children > 0 and not force:
        raise HTTPException(status_code=400, detail=f"Cannot delete: {children} classes exist. Use force=true to delete all children.")
    
    # If force=true, cascade delete all children
    if force and children > 0:
        await cascade_delete_division_children(code.upper())
    
    # Move to bin (soft delete)
    item.is_active = False
    item.is_deleted = True
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    await item.save()

    # Update parent's child count
    parent = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == item.sub_category_code)
    if parent:
        parent.child_count = await ItemDivision.find(
            ItemDivision.sub_category_code == parent.sub_category_code,
            ItemDivision.is_deleted == False
        ).count()
        await parent.save()

    return {"message": "Division moved to bin", "code": code, "children_deleted": children if force else 0}


# ==================== LEVEL 4: CLASSES ====================

@router.get("/classes", response_model=List[dict])
async def list_classes(
    category_code: Optional[str] = Query(None),
    sub_category_code: Optional[str] = Query(None),
    division_code: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List Level 4 classes"""
    
    query_conditions = []
    
    if category_code:
        query_conditions.append(ItemClass.category_code == category_code.upper())
    if sub_category_code:
        query_conditions.append(ItemClass.sub_category_code == sub_category_code.upper())
    if division_code:
        query_conditions.append(ItemClass.division_code == division_code.upper())
    if is_active is not None:
        query_conditions.append(ItemClass.is_active == is_active)
    
    if query_conditions:
        items = await ItemClass.find(*query_conditions).sort("sort_order").to_list()
    else:
        items = await ItemClass.find_all().sort("sort_order").to_list()
    
    return [
        {
            "id": str(i.id),
            "level": 4,
            "code": i.class_code,
            "name": i.class_name,
            "description": i.description,
            "category_code": i.category_code,
            "category_name": i.category_name,
            "sub_category_code": i.sub_category_code,
            "sub_category_name": i.sub_category_name,
            "division_code": i.division_code,
            "division_name": i.division_name,
            "path": i.path,
            "path_name": i.path_name,
            "hsn_code": i.hsn_code,
            "gst_rate": i.gst_rate,
            "icon": i.icon,
            "color_code": i.color_code,
            "sort_order": i.sort_order,
            "is_active": i.is_active,
            "child_count": i.child_count,
        }
        for i in items
    ]


@router.post("/classes", status_code=201)
async def create_class(data: ItemClassCreate):
    """Create a new Level 4 class"""
    
    cat = await ItemCategory.find_one(ItemCategory.category_code == data.category_code.upper())
    if not cat:
        raise HTTPException(status_code=400, detail=f"Category '{data.category_code}' not found")
    
    subcat = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data.sub_category_code.upper())
    if not subcat:
        raise HTTPException(status_code=400, detail=f"Sub-category '{data.sub_category_code}' not found")
    
    div = await ItemDivision.find_one(ItemDivision.division_code == data.division_code.upper())
    if not div:
        raise HTTPException(status_code=400, detail=f"Division '{data.division_code}' not found")
    
    existing = await ItemClass.find_one(ItemClass.class_code == data.class_code.upper())
    if existing:
        raise HTTPException(status_code=400, detail=f"Class '{data.class_code}' already exists")
    
    # Use insert() instead of save()
    item = await ItemClass(
        class_code=data.class_code.upper(),
        class_name=data.class_name,
        description=data.description,
        category_code=cat.category_code,
        category_name=cat.category_name,
        sub_category_code=subcat.sub_category_code,
        sub_category_name=subcat.sub_category_name,
        division_code=div.division_code,
        division_name=div.division_name,
        path=build_path([cat.category_code, subcat.sub_category_code, div.division_code, data.class_code.upper()]),
        path_name=build_path_name([cat.category_name, subcat.sub_category_name, div.division_name, data.class_name]),
        has_color=data.has_color,
        has_size=data.has_size,
        has_fabric=data.has_fabric,
        hsn_code=data.hsn_code,
        gst_rate=data.gst_rate,
        icon=data.icon,
        color_code=data.color_code,
        sort_order=data.sort_order,
    ).insert()
    
    div.child_count = await ItemClass.find(
        ItemClass.division_code == div.division_code,
        ItemClass.is_deleted == False
    ).count()
    await div.save()
    
    return {"message": "Class created", "code": item.class_code}


@router.put("/classes/{code}")
async def update_class(code: str, data: ItemClassUpdate):
    item = await ItemClass.find_one(ItemClass.class_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Class '{code}' not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    if data.class_name:
        item.path_name = build_path_name([item.category_name, item.sub_category_name, item.division_name, data.class_name])
    
    item.updated_at = datetime.utcnow()
    await item.save()
    
    return {"message": "Class updated", "code": item.class_code}


@router.delete("/classes/{code}")
async def delete_class(code: str, force: bool = Query(False, description="Force delete with all children")):
    """Soft delete a class with optional cascade deletion"""
    
    item = await ItemClass.find_one(ItemClass.class_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Class '{code}' not found")
    
    children = await ItemSubClass.find(
        ItemSubClass.class_code == code.upper(),
        ItemSubClass.is_deleted == False
    ).count()
    if children > 0 and not force:
        raise HTTPException(status_code=400, detail=f"Cannot delete: {children} sub-classes exist. Use force=true to delete all children.")
    
    # If force=true, cascade delete all children
    if force and children > 0:
        await cascade_delete_class_children(code.upper())
    
    # Move to bin (soft delete)
    item.is_active = False
    item.is_deleted = True
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    await item.save()

    # Update parent's child count
    parent = await ItemDivision.find_one(ItemDivision.division_code == item.division_code)
    if parent:
        parent.child_count = await ItemClass.find(
            ItemClass.division_code == parent.division_code,
            ItemClass.is_deleted == False
        ).count()
        await parent.save()

    return {"message": "Class moved to bin", "code": code, "children_deleted": children if force else 0}


# ==================== LEVEL 5: SUB-CLASSES ====================

@router.get("/sub-classes", response_model=List[dict])
async def list_sub_classes(
    category_code: Optional[str] = Query(None),
    sub_category_code: Optional[str] = Query(None),
    division_code: Optional[str] = Query(None),
    class_code: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    """List Level 5 sub-classes"""
    
    query_conditions = []
    
    if category_code:
        query_conditions.append(ItemSubClass.category_code == category_code.upper())
    if sub_category_code:
        query_conditions.append(ItemSubClass.sub_category_code == sub_category_code.upper())
    if division_code:
        query_conditions.append(ItemSubClass.division_code == division_code.upper())
    if class_code:
        query_conditions.append(ItemSubClass.class_code == class_code.upper())
    if is_active is not None:
        query_conditions.append(ItemSubClass.is_active == is_active)
    
    if query_conditions:
        items = await ItemSubClass.find(*query_conditions).sort("sort_order").to_list()
    else:
        items = await ItemSubClass.find_all().sort("sort_order").to_list()
    
    return [
        {
            "id": str(i.id),
            "level": 5,
            "code": i.sub_class_code,
            "name": i.sub_class_name,
            "description": i.description,
            "category_code": i.category_code,
            "category_name": i.category_name,
            "sub_category_code": i.sub_category_code,
            "sub_category_name": i.sub_category_name,
            "division_code": i.division_code,
            "division_name": i.division_name,
            "class_code": i.class_code,
            "class_name": i.class_name,
            "path": i.path,
            "path_name": i.path_name,
            "sku_prefix": getattr(i, 'sku_prefix', None) or i.sub_class_code,
            "last_sequence": getattr(i, 'last_sequence', 'A0000'),
            "hsn_code": i.hsn_code,
            "gst_rate": i.gst_rate,
            "icon": i.icon,
            "color_code": i.color_code,
            "sort_order": i.sort_order,
            "is_active": i.is_active,
            "item_count": i.item_count,
        }
        for i in items
    ]


@router.post("/sub-classes", status_code=201)
async def create_sub_class(data: ItemSubClassCreate):
    """Create a new Level 5 sub-class"""
    
    cat = await ItemCategory.find_one(ItemCategory.category_code == data.category_code.upper())
    if not cat:
        raise HTTPException(status_code=400, detail=f"Category '{data.category_code}' not found")
    
    subcat = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data.sub_category_code.upper())
    if not subcat:
        raise HTTPException(status_code=400, detail=f"Sub-category '{data.sub_category_code}' not found")
    
    div = await ItemDivision.find_one(ItemDivision.division_code == data.division_code.upper())
    if not div:
        raise HTTPException(status_code=400, detail=f"Division '{data.division_code}' not found")
    
    cls = await ItemClass.find_one(ItemClass.class_code == data.class_code.upper())
    if not cls:
        raise HTTPException(status_code=400, detail=f"Class '{data.class_code}' not found")
    
    existing = await ItemSubClass.find_one(ItemSubClass.sub_class_code == data.sub_class_code.upper())
    if existing:
        raise HTTPException(status_code=400, detail=f"Sub-class '{data.sub_class_code}' already exists")
    
    # Use insert() instead of save()
    item = await ItemSubClass(
        sub_class_code=data.sub_class_code.upper(),
        sub_class_name=data.sub_class_name,
        description=data.description,
        category_code=cat.category_code,
        category_name=cat.category_name,
        sub_category_code=subcat.sub_category_code,
        sub_category_name=subcat.sub_category_name,
        division_code=div.division_code,
        division_name=div.division_name,
        class_code=cls.class_code,
        class_name=cls.class_name,
        path=build_path([cat.category_code, subcat.sub_category_code, div.division_code, cls.class_code, data.sub_class_code.upper()]),
        path_name=build_path_name([cat.category_name, subcat.sub_category_name, div.division_name, cls.class_name, data.sub_class_name]),
        sku_prefix=data.sub_class_code.upper(),
        last_sequence="A0000",
        has_color=data.has_color,
        has_size=data.has_size,
        has_fabric=data.has_fabric,
        hsn_code=data.hsn_code,
        gst_rate=data.gst_rate,
        icon=data.icon,
        color_code=data.color_code,
        sort_order=data.sort_order,
    ).insert()
    
    cls.child_count = await ItemSubClass.find(
        ItemSubClass.class_code == cls.class_code,
        ItemSubClass.is_deleted == False
    ).count()
    await cls.save()
    
    return {"message": "Sub-class created", "code": item.sub_class_code}


@router.put("/sub-classes/{code}")
async def update_sub_class(code: str, data: ItemSubClassUpdate):
    item = await ItemSubClass.find_one(ItemSubClass.sub_class_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Sub-class '{code}' not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    if data.sub_class_name:
        item.path_name = build_path_name([item.category_name, item.sub_category_name, item.division_name, item.class_name, data.sub_class_name])
    
    item.updated_at = datetime.utcnow()
    await item.save()
    
    return {"message": "Sub-class updated", "code": item.sub_class_code}


@router.delete("/sub-classes/{code}")
async def delete_sub_class(code: str, force: bool = Query(False, description="Force delete with all children")):
    """Soft delete a sub-class (Level 5 has no children, so force parameter is optional)"""
    
    item = await ItemSubClass.find_one(ItemSubClass.sub_class_code == code.upper())
    if not item:
        raise HTTPException(status_code=404, detail=f"Sub-class '{code}' not found")
    
    # Move to bin (soft delete)
    item.is_active = False
    item.is_deleted = True
    item.deleted_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    await item.save()

    # Update parent's child count
    parent = await ItemClass.find_one(ItemClass.class_code == item.class_code)
    if parent:
        parent.child_count = await ItemSubClass.find(
            ItemSubClass.class_code == parent.class_code,
            ItemSubClass.is_deleted == False
        ).count()
        await parent.save()

    return {"message": "Sub-class moved to bin", "code": code}


# ==================== TREE VIEW ====================

@router.get("/tree")
async def get_hierarchy_tree(is_active: Optional[bool] = True):
    """Get full hierarchy as nested tree structure"""
    
    # Build base query for categories
    if is_active is not None:
        categories = await ItemCategory.find(
            ItemCategory.is_active == is_active
        ).sort("sort_order").to_list()
    else:
        categories = await ItemCategory.find_all().sort("sort_order").to_list()
    
    tree = []
    for cat in categories:
        cat_node = {
            "level": 1,
            "code": cat.category_code,
            "name": cat.category_name,
            "path": cat.category_code,
            "icon": cat.icon,
            "color_code": cat.color_code,
            "is_active": cat.is_active,
            "child_count": cat.child_count,
            "level_names": cat.level_names,
            "item_type": cat.item_type,
            "children": []
        }
        
        # Get sub-categories
        if is_active is not None:
            sub_cats = await ItemSubCategory.find(
                ItemSubCategory.category_code == cat.category_code,
                ItemSubCategory.is_active == is_active
            ).sort("sort_order").to_list()
        else:
            sub_cats = await ItemSubCategory.find(
                ItemSubCategory.category_code == cat.category_code
            ).sort("sort_order").to_list()
        
        for subcat in sub_cats:
            subcat_node = {
                "level": 2,
                "code": subcat.sub_category_code,
                "name": subcat.sub_category_name,
                "path": subcat.path,
                "icon": subcat.icon,
                "color_code": subcat.color_code,
                "is_active": subcat.is_active,
                "child_count": subcat.child_count,
                "children": []
            }
            
            # Get divisions
            if is_active is not None:
                divisions = await ItemDivision.find(
                    ItemDivision.sub_category_code == subcat.sub_category_code,
                    ItemDivision.is_active == is_active
                ).sort("sort_order").to_list()
            else:
                divisions = await ItemDivision.find(
                    ItemDivision.sub_category_code == subcat.sub_category_code
                ).sort("sort_order").to_list()
            
            for div in divisions:
                div_node = {
                    "level": 3,
                    "code": div.division_code,
                    "name": div.division_name,
                    "path": div.path,
                    "icon": div.icon,
                    "color_code": div.color_code,
                    "is_active": div.is_active,
                    "child_count": div.child_count,
                    "children": []
                }
                
                # Get classes
                if is_active is not None:
                    classes = await ItemClass.find(
                        ItemClass.division_code == div.division_code,
                        ItemClass.is_active == is_active
                    ).sort("sort_order").to_list()
                else:
                    classes = await ItemClass.find(
                        ItemClass.division_code == div.division_code
                    ).sort("sort_order").to_list()
                
                for cls in classes:
                    cls_node = {
                        "level": 4,
                        "code": cls.class_code,
                        "name": cls.class_name,
                        "path": cls.path,
                        "icon": cls.icon,
                        "color_code": cls.color_code,
                        "is_active": cls.is_active,
                        "child_count": cls.child_count,
                        "children": []
                    }
                    
                    # Get sub-classes
                    if is_active is not None:
                        sub_classes = await ItemSubClass.find(
                            ItemSubClass.class_code == cls.class_code,
                            ItemSubClass.is_active == is_active
                        ).sort("sort_order").to_list()
                    else:
                        sub_classes = await ItemSubClass.find(
                            ItemSubClass.class_code == cls.class_code
                        ).sort("sort_order").to_list()
                    
                    for subcls in sub_classes:
                        cls_node["children"].append({
                            "level": 5,
                            "code": subcls.sub_class_code,
                            "name": subcls.sub_class_name,
                            "path": subcls.path,
                            "icon": subcls.icon,
                            "color_code": subcls.color_code,
                            "is_active": subcls.is_active,
                            "item_count": subcls.item_count,
                            "children": []
                        })
                    
                    div_node["children"].append(cls_node)
                
                subcat_node["children"].append(div_node)
            
            cat_node["children"].append(subcat_node)
        
        tree.append(cat_node)
    
    return tree


# ==================== DROPDOWN HELPERS ====================

@router.get("/dropdown/{level}")
async def get_dropdown_options(
    level: int,
    category_code: Optional[str] = Query(None),
    sub_category_code: Optional[str] = Query(None),
    division_code: Optional[str] = Query(None),
    class_code: Optional[str] = Query(None),
):
    """Get dropdown options for a specific level, filtered by parent"""
    
    if level == 1:
        items = await ItemCategory.find(ItemCategory.is_active == True).sort("sort_order").to_list()
        return [{"value": i.category_code, "label": i.category_name, "color": i.color_code} for i in items]
    
    elif level == 2:
        if category_code:
            items = await ItemSubCategory.find(
                ItemSubCategory.category_code == category_code.upper(),
                ItemSubCategory.is_active == True
            ).sort("sort_order").to_list()
        else:
            items = await ItemSubCategory.find(ItemSubCategory.is_active == True).sort("sort_order").to_list()
        return [{"value": i.sub_category_code, "label": i.sub_category_name, "color": i.color_code} for i in items]
    
    elif level == 3:
        if sub_category_code:
            items = await ItemDivision.find(
                ItemDivision.sub_category_code == sub_category_code.upper(),
                ItemDivision.is_active == True
            ).sort("sort_order").to_list()
        else:
            items = await ItemDivision.find(ItemDivision.is_active == True).sort("sort_order").to_list()
        return [{"value": i.division_code, "label": i.division_name, "color": i.color_code} for i in items]
    
    elif level == 4:
        if division_code:
            items = await ItemClass.find(
                ItemClass.division_code == division_code.upper(),
                ItemClass.is_active == True
            ).sort("sort_order").to_list()
        else:
            items = await ItemClass.find(ItemClass.is_active == True).sort("sort_order").to_list()
        return [{"value": i.class_code, "label": i.class_name, "color": i.color_code} for i in items]
    
    elif level == 5:
        if class_code:
            items = await ItemSubClass.find(
                ItemSubClass.class_code == class_code.upper(),
                ItemSubClass.is_active == True
            ).sort("sort_order").to_list()
        else:
            items = await ItemSubClass.find(ItemSubClass.is_active == True).sort("sort_order").to_list()
        return [{"value": i.sub_class_code, "label": i.sub_class_name, "color": i.color_code} for i in items]
    
    return []


# ==================== SEED DATA ====================

@router.post("/seed")
async def seed_hierarchy():
    """Seed sample hierarchy data"""
    
    created = {"categories": 0, "sub_categories": 0, "divisions": 0, "classes": 0, "sub_classes": 0}
    
    # Seed categories
    for data in SEED_CATEGORIES:
        existing = await ItemCategory.find_one(ItemCategory.category_code == data["category_code"])
        if not existing:
            await ItemCategory(**data).insert()
            created["categories"] += 1
    
    # Seed sub-categories
    for data in SEED_SUB_CATEGORIES:
        existing = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data["sub_category_code"])
        if not existing:
            cat = await ItemCategory.find_one(ItemCategory.category_code == data["category_code"])
            if cat:
                await ItemSubCategory(
                    sub_category_code=data["sub_category_code"],
                    sub_category_name=data["sub_category_name"],
                    description=data.get("description"),
                    category_code=cat.category_code,
                    category_name=cat.category_name,
                    path=build_path([cat.category_code, data["sub_category_code"]]),
                    path_name=build_path_name([cat.category_name, data["sub_category_name"]]),
                    icon=data.get("icon", "Users"),
                    color_code=data.get("color_code", "#3b82f6"),
                    sort_order=data.get("sort_order", 0),
                ).insert()
                created["sub_categories"] += 1
    
    # Seed divisions
    for data in SEED_DIVISIONS:
        existing = await ItemDivision.find_one(ItemDivision.division_code == data["division_code"])
        if not existing:
            cat = await ItemCategory.find_one(ItemCategory.category_code == data["category_code"])
            subcat = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data["sub_category_code"])
            if cat and subcat:
                await ItemDivision(
                    division_code=data["division_code"],
                    division_name=data["division_name"],
                    description=data.get("description"),
                    category_code=cat.category_code,
                    category_name=cat.category_name,
                    sub_category_code=subcat.sub_category_code,
                    sub_category_name=subcat.sub_category_name,
                    path=build_path([cat.category_code, subcat.sub_category_code, data["division_code"]]),
                    path_name=build_path_name([cat.category_name, subcat.sub_category_name, data["division_name"]]),
                    icon=data.get("icon", "Layers"),
                    color_code=data.get("color_code", "#8b5cf6"),
                    sort_order=data.get("sort_order", 0),
                ).insert()
                created["divisions"] += 1
    
    # Seed classes
    for data in SEED_CLASSES:
        existing = await ItemClass.find_one(ItemClass.class_code == data["class_code"])
        if not existing:
            cat = await ItemCategory.find_one(ItemCategory.category_code == data["category_code"])
            subcat = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data["sub_category_code"])
            div = await ItemDivision.find_one(ItemDivision.division_code == data["division_code"])
            if cat and subcat and div:
                await ItemClass(
                    class_code=data["class_code"],
                    class_name=data["class_name"],
                    description=data.get("description"),
                    category_code=cat.category_code,
                    category_name=cat.category_name,
                    sub_category_code=subcat.sub_category_code,
                    sub_category_name=subcat.sub_category_name,
                    division_code=div.division_code,
                    division_name=div.division_name,
                    path=build_path([cat.category_code, subcat.sub_category_code, div.division_code, data["class_code"]]),
                    path_name=build_path_name([cat.category_name, subcat.sub_category_name, div.division_name, data["class_name"]]),
                    icon=data.get("icon", "Tag"),
                    color_code=data.get("color_code", "#ec4899"),
                    sort_order=data.get("sort_order", 0),
                ).insert()
                created["classes"] += 1
    
    # Seed sub-classes
    for data in SEED_SUB_CLASSES:
        existing = await ItemSubClass.find_one(ItemSubClass.sub_class_code == data["sub_class_code"])
        if not existing:
            cat = await ItemCategory.find_one(ItemCategory.category_code == data["category_code"])
            subcat = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == data["sub_category_code"])
            div = await ItemDivision.find_one(ItemDivision.division_code == data["division_code"])
            cls = await ItemClass.find_one(ItemClass.class_code == data["class_code"])
            if cat and subcat and div and cls:
                await ItemSubClass(
                    sub_class_code=data["sub_class_code"],
                    sub_class_name=data["sub_class_name"],
                    description=data.get("description"),
                    category_code=cat.category_code,
                    category_name=cat.category_name,
                    sub_category_code=subcat.sub_category_code,
                    sub_category_name=subcat.sub_category_name,
                    division_code=div.division_code,
                    division_name=div.division_name,
                    class_code=cls.class_code,
                    class_name=cls.class_name,
                    path=build_path([cat.category_code, subcat.sub_category_code, div.division_code, cls.class_code, data["sub_class_code"]]),
                    path_name=build_path_name([cat.category_name, subcat.sub_category_name, div.division_name, cls.class_name, data["sub_class_name"]]),
                    sku_prefix=data["sub_class_code"],
                    icon=data.get("icon", "Hash"),
                    color_code=data.get("color_code", "#f59e0b"),
                    sort_order=data.get("sort_order", 0),
                ).insert()
                created["sub_classes"] += 1
    
    # Update child counts (exclude deleted items)
    for cat in await ItemCategory.find_all().to_list():
        cat.child_count = await ItemSubCategory.find(
            ItemSubCategory.category_code == cat.category_code,
            ItemSubCategory.is_deleted == False
        ).count()
        await cat.save()

    for subcat in await ItemSubCategory.find_all().to_list():
        subcat.child_count = await ItemDivision.find(
            ItemDivision.sub_category_code == subcat.sub_category_code,
            ItemDivision.is_deleted == False
        ).count()
        await subcat.save()

    for div in await ItemDivision.find_all().to_list():
        div.child_count = await ItemClass.find(
            ItemClass.division_code == div.division_code,
            ItemClass.is_deleted == False
        ).count()
        await div.save()

    for cls in await ItemClass.find_all().to_list():
        cls.child_count = await ItemSubClass.find(
            ItemSubClass.class_code == cls.class_code,
            ItemSubClass.is_deleted == False
        ).count()
        await cls.save()
    
    return {"message": "Hierarchy seeded", "created": created}


# ==================== CASCADE DELETION HELPERS ====================

async def cascade_delete_category_children(category_code: str):
    """Recursively delete all children of a category"""
    sub_categories = await ItemSubCategory.find(
        ItemSubCategory.category_code == category_code,
        ItemSubCategory.is_deleted == False
    ).to_list()

    for sub_cat in sub_categories:
        await cascade_delete_sub_category_children(sub_cat.sub_category_code)
        # Move sub-category to bin
        sub_cat.is_active = False
        sub_cat.is_deleted = True
        sub_cat.deleted_at = datetime.utcnow()
        await sub_cat.save()


async def cascade_delete_sub_category_children(sub_category_code: str):
    """Recursively delete all children of a sub-category"""
    divisions = await ItemDivision.find(
        ItemDivision.sub_category_code == sub_category_code,
        ItemDivision.is_deleted == False
    ).to_list()

    for div in divisions:
        await cascade_delete_division_children(div.division_code)
        # Move division to bin
        div.is_active = False
        div.is_deleted = True
        div.deleted_at = datetime.utcnow()
        await div.save()


async def cascade_delete_division_children(division_code: str):
    """Recursively delete all children of a division"""
    classes = await ItemClass.find(
        ItemClass.division_code == division_code,
        ItemClass.is_deleted == False
    ).to_list()

    for cls in classes:
        await cascade_delete_class_children(cls.class_code)
        # Move class to bin
        cls.is_active = False
        cls.is_deleted = True
        cls.deleted_at = datetime.utcnow()
        await cls.save()


async def cascade_delete_class_children(class_code: str):
    """Delete all sub-classes of a class"""
    sub_classes = await ItemSubClass.find(
        ItemSubClass.class_code == class_code,
        ItemSubClass.is_deleted == False
    ).to_list()

    for sub_cls in sub_classes:
        # Move sub-class to bin
        sub_cls.is_active = False
        sub_cls.is_deleted = True
        sub_cls.deleted_at = datetime.utcnow()
        await sub_cls.save()


# ==================== BIN MANAGEMENT ROUTES ====================

@router.get("/bin", response_model=List[dict])
async def list_bin_items():
    """List all deleted category hierarchy items in the bin"""
    
    deleted_categories = await ItemCategory.find(ItemCategory.is_deleted == True).to_list()
    deleted_sub_categories = await ItemSubCategory.find(ItemSubCategory.is_deleted == True).to_list()
    deleted_divisions = await ItemDivision.find(ItemDivision.is_deleted == True).to_list()
    deleted_classes = await ItemClass.find(ItemClass.is_deleted == True).to_list()
    deleted_sub_classes = await ItemSubClass.find(ItemSubClass.is_deleted == True).to_list()
    
    bin_items = []
    
    # Add categories
    for item in deleted_categories:
        bin_items.append({
            "id": item.category_code,
            "name": item.category_name,
            "type": "category",
            "level": 1,
            "deleted_at": item.deleted_at,
            "path_name": item.category_name  # Level 1 categories don't have path_name
        })
    
    # Add sub-categories
    for item in deleted_sub_categories:
        bin_items.append({
            "id": item.sub_category_code,
            "name": item.sub_category_name,
            "type": "sub-category",
            "level": 2,
            "deleted_at": item.deleted_at,
            "path_name": item.path_name
        })
    
    # Add divisions
    for item in deleted_divisions:
        bin_items.append({
            "id": item.division_code,
            "name": item.division_name,
            "type": "division",
            "level": 3,
            "deleted_at": item.deleted_at,
            "path_name": item.path_name
        })
    
    # Add classes
    for item in deleted_classes:
        bin_items.append({
            "id": item.class_code,
            "name": item.class_name,
            "type": "class",
            "level": 4,
            "deleted_at": item.deleted_at,
            "path_name": item.path_name
        })
    
    # Add sub-classes
    for item in deleted_sub_classes:
        bin_items.append({
            "id": item.sub_class_code,
            "name": item.sub_class_name,
            "type": "sub-class",
            "level": 5,
            "deleted_at": item.deleted_at,
            "path_name": item.path_name
        })
    
    # Sort by deleted_at descending
    bin_items.sort(key=lambda x: x['deleted_at'], reverse=True)
    
    return bin_items


@router.post("/bin/restore/{item_type}/{code}")
async def restore_from_bin(item_type: str, code: str):
    """Restore an item from bin"""
    
    code = code.upper()
    
    if item_type == "category":
        item = await ItemCategory.find_one(ItemCategory.category_code == code)
    elif item_type == "sub-category":
        item = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == code)
    elif item_type == "division":
        item = await ItemDivision.find_one(ItemDivision.division_code == code)
    elif item_type == "class":
        item = await ItemClass.find_one(ItemClass.class_code == code)
    elif item_type == "sub-class":
        item = await ItemSubClass.find_one(ItemSubClass.sub_class_code == code)
    else:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    if not item:
        raise HTTPException(status_code=404, detail=f"{item_type.title()} '{code}' not found")
    
    if not item.is_deleted:
        raise HTTPException(status_code=400, detail=f"{item_type.title()} '{code}' is not in bin")
    
    # Restore item
    item.is_active = True
    item.is_deleted = False
    item.deleted_at = None
    item.updated_at = datetime.utcnow()
    await item.save()

    # Update parent's child count after restoration
    if item_type == "sub-category":
        parent = await ItemCategory.find_one(ItemCategory.category_code == item.category_code)
        if parent:
            parent.child_count = await ItemSubCategory.find(
                ItemSubCategory.category_code == parent.category_code,
                ItemSubCategory.is_deleted == False
            ).count()
            await parent.save()
    elif item_type == "division":
        parent = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == item.sub_category_code)
        if parent:
            parent.child_count = await ItemDivision.find(
                ItemDivision.sub_category_code == parent.sub_category_code,
                ItemDivision.is_deleted == False
            ).count()
            await parent.save()
    elif item_type == "class":
        parent = await ItemDivision.find_one(ItemDivision.division_code == item.division_code)
        if parent:
            parent.child_count = await ItemClass.find(
                ItemClass.division_code == parent.division_code,
                ItemClass.is_deleted == False
            ).count()
            await parent.save()
    elif item_type == "sub-class":
        parent = await ItemClass.find_one(ItemClass.class_code == item.class_code)
        if parent:
            parent.child_count = await ItemSubClass.find(
                ItemSubClass.class_code == parent.class_code,
                ItemSubClass.is_deleted == False
            ).count()
            await parent.save()

    return {"message": f"{item_type.title()} restored from bin", "code": code}


@router.delete("/bin/permanent/{item_type}/{code}")
async def permanent_delete_from_bin(item_type: str, code: str):
    """Permanently delete an item from bin"""
    
    code = code.upper()
    
    if item_type == "category":
        item = await ItemCategory.find_one(ItemCategory.category_code == code)
    elif item_type == "sub-category":
        item = await ItemSubCategory.find_one(ItemSubCategory.sub_category_code == code)
    elif item_type == "division":
        item = await ItemDivision.find_one(ItemDivision.division_code == code)
    elif item_type == "class":
        item = await ItemClass.find_one(ItemClass.class_code == code)
    elif item_type == "sub-class":
        item = await ItemSubClass.find_one(ItemSubClass.sub_class_code == code)
    else:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    if not item:
        raise HTTPException(status_code=404, detail=f"{item_type.title()} '{code}' not found")
    
    if not item.is_deleted:
        raise HTTPException(status_code=400, detail=f"{item_type.title()} '{code}' is not in bin")
    
    # Permanently delete
    await item.delete()
    
    return {"message": f"{item_type.title()} permanently deleted", "code": code}
