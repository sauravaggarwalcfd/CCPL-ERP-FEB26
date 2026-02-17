"""
Specifications API Routes
CRUD operations for category specifications and item specifications
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..models.specifications import (
    CategorySpecifications,
    ItemSpecifications,
    CategorySpecificationsRequest,
    CategorySpecificationsResponse,
    ItemSpecificationsRequest,
    ItemSpecificationsResponse,
    VariantFieldConfigRequest,
    CustomFieldConfigRequest,
    FormField,
    FieldOption,
    create_default_variant_field_config,
    create_default_specifications_config,
    VariantFieldConfig,
    CustomFieldConfig,
    FieldSource
)
from ..models.colour_master import ColourMaster
from ..models.size_master import SizeMaster
from ..models.uom_master import UOMMaster
# Assuming supplier model exists
# from ..models.supplier import Supplier

router = APIRouter()
logger = logging.getLogger(__name__)


def spec_to_response(spec: CategorySpecifications) -> CategorySpecificationsResponse:
    """Convert CategorySpecifications document to response"""
    return CategorySpecificationsResponse(
        id=str(spec.id),
        category_code=spec.category_code,
        category_name=spec.category_name,
        category_level=spec.category_level,
        specifications=spec.specifications.model_dump() if spec.specifications else {},
        custom_fields=spec.custom_fields,
        is_active=spec.is_active,
        created_by=spec.created_by,
        created_date=spec.created_date,
        last_modified_by=spec.last_modified_by,
        last_modified_date=spec.last_modified_date
    )


def item_spec_to_response(item_spec: ItemSpecifications) -> ItemSpecificationsResponse:
    """Convert ItemSpecifications document to response"""
    return ItemSpecificationsResponse(
        id=str(item_spec.id),
        item_code=item_spec.item_code,
        category_code=item_spec.category_code,
        colour_code=item_spec.colour_code,
        size_code=item_spec.size_code,
        uom_code=item_spec.uom_code,
        vendor_code=item_spec.vendor_code,
        custom_field_values=item_spec.custom_field_values,
        created_date=item_spec.created_date,
        last_modified_date=item_spec.last_modified_date
    )


# ==================== LIST ALL SPECIFICATIONS ====================

@router.get("/specifications", response_model=List[CategorySpecificationsResponse])
async def list_specifications(
    is_active: Optional[bool] = Query(None)
):
    """List all category specifications"""
    query = {}
    if is_active is not None:
        query["is_active"] = is_active

    specs = await CategorySpecifications.find(query).sort("+category_name").to_list()
    return [spec_to_response(s) for s in specs]


# ==================== GET SPECIFICATION BY CATEGORY ====================

@router.get("/specifications/{category_code}", response_model=CategorySpecificationsResponse)
async def get_specifications(category_code: str):
    """Get specification configuration for a specific category"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    return spec_to_response(spec)


# ==================== CREATE/UPDATE SPECIFICATIONS ====================

@router.post("/specifications/{category_code}", response_model=CategorySpecificationsResponse)
async def create_or_update_specifications(
    category_code: str,
    data: CategorySpecificationsRequest
):
    """Create or update specifications for a category"""
    # Check if exists
    existing = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if existing:
        # Update existing
        # Update specifications
        if data.specifications:
            spec_dict = {}
            for field_key, field_config in data.specifications.items():
                if field_key in ["colour", "size", "uom", "vendor"]:
                    # Get source
                    source_map = {
                        "colour": FieldSource.COLOUR_MASTER,
                        "size": FieldSource.SIZE_MASTER,
                        "uom": FieldSource.UOM_MASTER,
                        "vendor": FieldSource.SUPPLIER_MASTER
                    }

                    spec_dict[field_key] = VariantFieldConfig(
                        enabled=field_config.enabled,
                        required=field_config.required,
                        field_name=field_key.title(),
                        field_type="SELECT",
                        field_key=f"{field_key}_code",
                        source=source_map[field_key],
                        groups=field_config.groups,
                        allow_multiple=field_config.allow_multiple,
                        default_value=field_config.default_value
                    )

            existing.specifications.colour = spec_dict.get("colour")
            existing.specifications.size = spec_dict.get("size")
            existing.specifications.uom = spec_dict.get("uom")
            existing.specifications.vendor = spec_dict.get("vendor")

        # Update custom fields
        if data.custom_fields:
            existing.custom_fields = [
                CustomFieldConfig(
                    field_code=cf.field_code,
                    field_name=cf.field_name,
                    field_type=cf.field_type,
                    field_key=cf.field_code.lower(),
                    enabled=cf.enabled,
                    required=cf.required,
                    options=cf.options,
                    default_value=cf.default_value,
                    placeholder=cf.placeholder,
                    min_value=cf.min_value,
                    max_value=cf.max_value,
                    display_order=cf.display_order
                )
                for cf in data.custom_fields
            ]

        existing.category_name = data.category_name
        existing.category_level = data.category_level
        existing.last_modified_date = datetime.utcnow()
        await existing.save()

        logger.info(f"Updated specifications for category: {category_code}")
        return spec_to_response(existing)

    else:
        # Create new
        spec_config = create_default_specifications_config()

        # Apply provided configurations
        if data.specifications:
            for field_key, field_config in data.specifications.items():
                if field_key in ["colour", "size", "uom", "vendor"]:
                    source_map = {
                        "colour": FieldSource.COLOUR_MASTER,
                        "size": FieldSource.SIZE_MASTER,
                        "uom": FieldSource.UOM_MASTER,
                        "vendor": FieldSource.SUPPLIER_MASTER
                    }

                    variant_config = VariantFieldConfig(
                        enabled=field_config.enabled,
                        required=field_config.required,
                        field_name=field_key.title(),
                        field_type="SELECT",
                        field_key=f"{field_key}_code",
                        source=source_map[field_key],
                        groups=field_config.groups,
                        allow_multiple=field_config.allow_multiple,
                        default_value=field_config.default_value
                    )

                    setattr(spec_config, field_key, variant_config)

        custom_fields = []
        if data.custom_fields:
            custom_fields = [
                CustomFieldConfig(
                    field_code=cf.field_code,
                    field_name=cf.field_name,
                    field_type=cf.field_type,
                    field_key=cf.field_code.lower(),
                    enabled=cf.enabled,
                    required=cf.required,
                    options=cf.options,
                    default_value=cf.default_value,
                    placeholder=cf.placeholder,
                    min_value=cf.min_value,
                    max_value=cf.max_value,
                    display_order=cf.display_order
                )
                for cf in data.custom_fields
            ]

        spec = CategorySpecifications(
            category_code=category_code.upper(),
            category_name=data.category_name,
            category_level=data.category_level,
            specifications=spec_config,
            custom_fields=custom_fields
        )

        await spec.insert()
        logger.info(f"Created specifications for category: {category_code}")
        return spec_to_response(spec)


# ==================== UPDATE VARIANT FIELD ====================

@router.put("/specifications/{category_code}/variant/{field}")
async def update_variant_field(
    category_code: str,
    field: str,
    config: VariantFieldConfigRequest
):
    """Enable/disable or update a variant field"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    if field not in ["colour", "size", "uom", "vendor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field '{field}'. Must be one of: colour, size, uom, vendor"
        )

    # Get source
    source_map = {
        "colour": FieldSource.COLOUR_MASTER,
        "size": FieldSource.SIZE_MASTER,
        "uom": FieldSource.UOM_MASTER,
        "vendor": FieldSource.SUPPLIER_MASTER
    }

    # Update field config
    field_config = VariantFieldConfig(
        enabled=config.enabled,
        required=config.required,
        field_name=field.title(),
        field_type="SELECT",
        field_key=f"{field}_code",
        source=source_map[field],
        groups=config.groups,
        allow_multiple=config.allow_multiple,
        default_value=config.default_value
    )

    setattr(spec.specifications, field, field_config)
    spec.last_modified_date = datetime.utcnow()
    await spec.save()

    logger.info(f"Updated variant field '{field}' for category: {category_code}")
    return {"message": f"Variant field '{field}' updated successfully"}


# ==================== DELETE VARIANT FIELD ====================

@router.delete("/specifications/{category_code}/variant/{field}")
async def delete_variant_field(category_code: str, field: str):
    """Remove (disable) a variant field"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    if field not in ["colour", "size", "uom", "vendor"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field '{field}'"
        )

    # Disable field
    field_config = getattr(spec.specifications, field)
    if field_config:
        field_config.enabled = False
        spec.last_modified_date = datetime.utcnow()
        await spec.save()

    logger.info(f"Disabled variant field '{field}' for category: {category_code}")
    return {"message": f"Variant field '{field}' disabled"}


# ==================== CUSTOM FIELD MANAGEMENT ====================

@router.post("/specifications/{category_code}/custom-field")
async def add_custom_field(category_code: str, field: CustomFieldConfigRequest):
    """Add a custom field to category specifications"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    # Check if field code already exists
    if any(cf.field_code == field.field_code for cf in spec.custom_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Custom field '{field.field_code}' already exists"
        )

    custom_field = CustomFieldConfig(
        field_code=field.field_code,
        field_name=field.field_name,
        field_type=field.field_type,
        field_key=field.field_code.lower(),
        enabled=field.enabled,
        required=field.required,
        options=field.options,
        default_value=field.default_value,
        placeholder=field.placeholder,
        min_value=field.min_value,
        max_value=field.max_value,
        display_order=field.display_order
    )

    spec.custom_fields.append(custom_field)
    spec.last_modified_date = datetime.utcnow()
    await spec.save()

    logger.info(f"Added custom field '{field.field_code}' to category: {category_code}")
    return {"message": "Custom field added successfully", "field": custom_field}


@router.put("/specifications/{category_code}/custom-field/{field_code}")
async def update_custom_field(
    category_code: str,
    field_code: str,
    field: CustomFieldConfigRequest
):
    """Update a custom field"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    # Find and update custom field
    field_found = False
    for i, cf in enumerate(spec.custom_fields):
        if cf.field_code == field_code:
            spec.custom_fields[i] = CustomFieldConfig(
                field_code=field.field_code,
                field_name=field.field_name,
                field_type=field.field_type,
                field_key=field.field_code.lower(),
                enabled=field.enabled,
                required=field.required,
                options=field.options,
                default_value=field.default_value,
                placeholder=field.placeholder,
                min_value=field.min_value,
                max_value=field.max_value,
                display_order=field.display_order
            )
            field_found = True
            break

    if not field_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom field '{field_code}' not found"
        )

    spec.last_modified_date = datetime.utcnow()
    await spec.save()

    logger.info(f"Updated custom field '{field_code}' for category: {category_code}")
    return {"message": "Custom field updated successfully"}


@router.delete("/specifications/{category_code}/custom-field/{field_code}")
async def delete_custom_field(category_code: str, field_code: str):
    """Remove a custom field"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    # Remove custom field
    original_count = len(spec.custom_fields)
    spec.custom_fields = [cf for cf in spec.custom_fields if cf.field_code != field_code]

    if len(spec.custom_fields) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom field '{field_code}' not found"
        )

    spec.last_modified_date = datetime.utcnow()
    await spec.save()

    logger.info(f"Deleted custom field '{field_code}' from category: {category_code}")
    return {"message": "Custom field deleted successfully"}


# ==================== FORM FIELDS RETRIEVAL ====================

@router.get("/specifications/{category_code}/form-fields", response_model=List[FormField])
async def get_form_fields(category_code: str):
    """Get all form fields for a category (for UI rendering)"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    fields = []

    # Add variant fields
    if spec.specifications:
        for field_name in ["colour", "size", "uom", "vendor"]:
            field_config = getattr(spec.specifications, field_name)
            if field_config and field_config.enabled:
                fields.append(FormField(
                    field_key=field_config.field_key,
                    field_name=field_config.field_name,
                    field_type=field_config.field_type,
                    required=field_config.required,
                    enabled=field_config.enabled,
                    default_value=field_config.default_value,
                    source=field_config.source.value,
                    groups=field_config.groups,
                    display_order=0
                ))

    # Add custom fields
    for cf in spec.custom_fields:
        if cf.enabled:
            fields.append(FormField(
                field_key=cf.field_key,
                field_name=cf.field_name,
                field_type=cf.field_type.value,
                required=cf.required,
                enabled=cf.enabled,
                options=[FieldOption(code=opt, name=opt) for opt in cf.options],
                default_value=cf.default_value,
                placeholder=cf.placeholder,
                min_value=cf.min_value,
                max_value=cf.max_value,
                display_order=cf.display_order
            ))

    # Sort by display_order
    fields.sort(key=lambda x: x.display_order)

    return fields


# ==================== FIELD VALUES RETRIEVAL ====================

@router.get("/specifications/{category_code}/field-values/{field_key}")
async def get_field_values(category_code: str, field_key: str):
    """Get dropdown options for a specific field"""
    spec = await CategorySpecifications.find_one(
        CategorySpecifications.category_code == category_code.upper()
    )

    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for category '{category_code}' not found"
        )

    # Determine field source
    field_config = None
    if field_key in ["colour", "colour_code"]:
        field_config = spec.specifications.colour
    elif field_key in ["size", "size_code"]:
        field_config = spec.specifications.size
    elif field_key in ["uom", "uom_code"]:
        field_config = spec.specifications.uom
    elif field_key in ["vendor", "vendor_code"]:
        field_config = spec.specifications.vendor

    if not field_config or not field_config.enabled:
        return []

    # Fetch values based on source
    options = []

    if field_config.source == FieldSource.COLOUR_MASTER:
        query = {"is_active": True}
        if field_config.groups:
            query["colour_group"] = {"$in": field_config.groups}

        colours = await ColourMaster.find(query).sort("+display_order").to_list()
        options = [
            FieldOption(
                code=c.colour_code,
                name=c.colour_name,
                additional_info={"hex": c.colour_hex, "group": c.colour_group}
            )
            for c in colours
        ]

    elif field_config.source == FieldSource.SIZE_MASTER:
        query = {"is_active": True}
        if field_config.groups:
            query["size_group"] = {"$in": field_config.groups}

        sizes = await SizeMaster.find(query).sort("+display_order").to_list()
        options = [
            FieldOption(
                code=s.size_code,
                name=s.size_name,
                additional_info={"group": s.size_group, "numeric_value": s.numeric_value}
            )
            for s in sizes
        ]

    elif field_config.source == FieldSource.UOM_MASTER:
        query = {"is_active": True}
        if field_config.groups:
            query["uom_group"] = {"$in": field_config.groups}

        uoms = await UOMMaster.find(query).sort("+display_order").to_list()
        options = [
            FieldOption(
                code=u.uom_code,
                name=f"{u.uom_name} ({u.uom_symbol})",
                additional_info={"symbol": u.uom_symbol, "group": u.uom_group}
            )
            for u in uoms
        ]

    elif field_config.source == FieldSource.SUPPLIER_MASTER:
        # TODO: Implement when Supplier model is available
        # For now, return empty list
        options = []

    return options


# ==================== ITEM SPECIFICATIONS ====================

@router.get("/items/{item_code}/specifications", response_model=ItemSpecificationsResponse)
async def get_item_specifications(item_code: str):
    """Get specifications for a specific item"""
    item_spec = await ItemSpecifications.find_one(
        ItemSpecifications.item_code == item_code.upper()
    )

    if not item_spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for item '{item_code}' not found"
        )

    return item_spec_to_response(item_spec)


@router.post("/items/{item_code}/specifications", response_model=ItemSpecificationsResponse)
async def create_or_update_item_specifications(
    item_code: str,
    category_code: str,
    data: ItemSpecificationsRequest
):
    """Create or update specifications for an item"""
    # Check if exists
    existing = await ItemSpecifications.find_one(
        ItemSpecifications.item_code == item_code.upper()
    )

    if existing:
        # Update existing
        existing.colour_code = data.colour_code
        existing.size_code = data.size_code
        existing.uom_code = data.uom_code
        existing.vendor_code = data.vendor_code
        existing.custom_field_values = data.custom_field_values
        existing.last_modified_date = datetime.utcnow()
        await existing.save()

        logger.info(f"Updated specifications for item: {item_code}")
        return item_spec_to_response(existing)

    else:
        # Create new
        item_spec = ItemSpecifications(
            item_code=item_code.upper(),
            category_code=category_code.upper(),
            colour_code=data.colour_code,
            size_code=data.size_code,
            uom_code=data.uom_code,
            vendor_code=data.vendor_code,
            custom_field_values=data.custom_field_values
        )

        await item_spec.insert()
        logger.info(f"Created specifications for item: {item_code}")
        return item_spec_to_response(item_spec)


@router.delete("/items/{item_code}/specifications")
async def delete_item_specifications(item_code: str):
    """Delete specifications for an item"""
    item_spec = await ItemSpecifications.find_one(
        ItemSpecifications.item_code == item_code.upper()
    )

    if not item_spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specifications for item '{item_code}' not found"
        )

    await item_spec.delete()
    logger.info(f"Deleted specifications for item: {item_code}")
    return {"message": "Item specifications deleted successfully"}


# ==================== QUERY ITEMS BY SPECIFICATIONS ====================

@router.get("/items/by-specifications")
async def query_items_by_specifications(
    category_code: Optional[str] = None,
    colour_code: Optional[str] = None,
    size_code: Optional[str] = None,
    uom_code: Optional[str] = None,
    vendor_code: Optional[str] = None
):
    """Query items by specification values"""
    query = {}

    if category_code:
        query["category_code"] = category_code.upper()
    if colour_code:
        query["colour_code"] = colour_code.upper()
    if size_code:
        query["size_code"] = size_code.upper()
    if uom_code:
        query["uom_code"] = uom_code.upper()
    if vendor_code:
        query["vendor_code"] = vendor_code.upper()

    items = await ItemSpecifications.find(query).to_list()
    return [item_spec_to_response(item) for item in items]
