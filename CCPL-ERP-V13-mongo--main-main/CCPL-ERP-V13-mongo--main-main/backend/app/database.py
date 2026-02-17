"""Database layer — Google Sheets backed (replaces MongoDB/Beanie)."""
import logging
from .config import settings
from .services.sheets_db_service import SheetsDBService, get_sheets_db, init_sheets_db

logger = logging.getLogger(__name__)

# Tab schemas: tab_name -> list of column headers
TAB_SCHEMAS = {
    '_users': ['_id', 'email', 'password_hash', 'full_name', 'phone', 'avatar',
               'role', 'additional_permissions', 'denied_permissions', 'effective_permissions',
               'team_id', 'team_name', 'manager', 'assigned_warehouses', 'status',
               'security', 'sessions', 'invitation', 'preferences',
               'last_login', 'last_active', 'login_count', 'created_by', 'created_at', 'updated_at'],
    '_roles': ['_id', 'name', 'slug', 'description', 'permission_ids', 'permission_codes',
               'level', 'warehouse_access', 'data_scope', 'is_active', 'created_at', 'updated_at'],
    '_permissions': ['_id', 'code', 'name', 'module', 'action', 'description'],
    '_item_types': ['_id', 'type_code', 'type_name', 'description', 'allow_purchase', 'allow_sale',
                    'track_inventory', 'require_quality_check', 'default_uom', 'color_code', 'icon',
                    'sort_order', 'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at'],
    '_categories': ['_id', 'category_code', 'category_name', 'description', 'path', 'path_name',
                    'child_count', 'is_active', 'deleted_at', 'created_at', 'updated_at'],
    '_sub_categories': ['_id', 'sub_category_code', 'sub_category_name', 'category_code', 'category_name',
                        'description', 'path', 'path_name', 'child_count', 'is_active', 'deleted_at',
                        'created_at', 'updated_at'],
    '_divisions': ['_id', 'division_code', 'division_name', 'sub_category_code', 'sub_category_name',
                   'description', 'path', 'path_name', 'child_count', 'is_active', 'deleted_at',
                   'created_at', 'updated_at'],
    '_classes': ['_id', 'class_code', 'class_name', 'division_code', 'division_name',
                 'description', 'path', 'path_name', 'child_count', 'is_active', 'deleted_at',
                 'created_at', 'updated_at'],
    '_sub_classes': ['_id', 'sub_class_code', 'sub_class_name', 'class_code', 'class_name',
                     'description', 'path', 'path_name', 'is_active', 'deleted_at',
                     'created_at', 'updated_at'],
    '_colour_master': ['_id', 'colour_code', 'colour_name', 'colour_hex', 'rgb_value',
                       'colour_group', 'group_name', 'is_active', 'deleted_at', 'created_at', 'updated_at'],
    '_size_master': ['_id', 'size_code', 'size_name', 'size_group', 'group_name',
                     'numeric_value', 'sort_order', 'is_active', 'deleted_at', 'created_at', 'updated_at'],
    '_uom_master': ['_id', 'uom_code', 'uom_name', 'uom_symbol', 'uom_group', 'group_name',
                    'conversion_to_base', 'is_base_uom', 'is_active', 'deleted_at', 'created_at', 'updated_at'],
    '_variant_groups': ['_id', 'variant_type', 'group_code', 'group_name', 'description',
                        'sort_order', 'is_active', 'created_at', 'updated_at'],
    '_brand_master': ['_id', 'brand_code', 'brand_name', 'brand_category', 'description',
                      'logo_url', 'is_active', 'deleted_at', 'created_by', 'created_at', 'updated_at'],
    '_supplier_master': ['_id', 'supplier_code', 'supplier_name', 'supplier_type', 'contact_person',
                         'email', 'phone', 'address', 'city', 'state', 'country', 'pin_code',
                         'gst_number', 'pan_number', 'payment_terms', 'credit_limit', 'bank_details',
                         'is_active', 'deleted_at', 'created_by', 'created_at', 'updated_at'],
    '_item_master': ['_id', 'item_code', 'item_name', 'item_description', 'item_type_code', 'item_type_name',
                     'category_code', 'category_name', 'sub_category_code', 'sub_category_name',
                     'division_code', 'division_name', 'class_code', 'class_name',
                     'sub_class_code', 'sub_class_name', 'hierarchy_path', 'hierarchy_path_name',
                     'brand_code', 'brand_name', 'colour_code', 'colour_name', 'size_code', 'size_name',
                     'uom_code', 'uom_name', 'purchase_uom', 'sale_uom', 'inventory_type',
                     'mrp', 'purchase_price', 'selling_price', 'min_stock', 'max_stock', 'reorder_level',
                     'current_stock', 'hsn_code', 'tax_rate', 'image_url', 'image_base64',
                     'notes', 'is_active', 'deleted_at', 'created_by', 'created_at', 'updated_at'],
    '_products': ['_id', 'style_number', 'name', 'description', 'category', 'brand', 'season',
                  'base_cost', 'base_price', 'variants', 'images', 'is_active',
                  'created_at', 'updated_at'],
    '_purchase_orders': ['_id', 'po_number', 'po_date', 'expected_date', 'po_status',
                         'supplier', 'items', 'summary', 'delivery', 'payment', 'approval', 'tracking',
                         'notes', 'internal_notes', 'terms_conditions', 'is_deleted',
                         'created_by', 'updated_by', 'created_at', 'updated_at'],
    '_category_specs': ['_id', 'category_code', 'variant_fields', 'custom_fields',
                        'created_at', 'updated_at'],
    '_item_specs': ['_id', 'item_code', 'category_code', 'colour_code', 'colour_name',
                    'size_code', 'size_name', 'uom_code', 'uom_name', 'brand_code', 'brand_name',
                    'custom_values', 'created_at', 'updated_at'],
    '_file_master': ['_id', 'file_id', 'original_name', 'stored_name', 'file_path',
                     'file_url', 'thumbnail_path', 'thumbnail_url', 'file_size', 'file_type',
                     'mime_type', 'category', 'description', 'tags', 'metadata',
                     'uploaded_by', 'upload_date', 'is_active'],
    '_md_categories': ['_id', 'name', 'slug', 'description', 'parent_id', 'is_active',
                       'created_at', 'updated_at'],
    '_md_brands': ['_id', 'name', 'slug', 'description', 'logo_url', 'is_active',
                   'created_at', 'updated_at'],
    '_md_seasons': ['_id', 'name', 'full_name', 'start_date', 'end_date', 'is_active',
                    'created_at', 'updated_at'],
    '_md_colors': ['_id', 'code', 'name', 'hex_value', 'is_active', 'created_at', 'updated_at'],
    '_md_sizes': ['_id', 'name', 'type', 'sort_order', 'is_active', 'created_at', 'updated_at'],
    '_customers': ['_id', 'code', 'customer_type', 'name', 'email', 'phone', 'addresses',
                   'credit_limit', 'current_balance', 'loyalty_points', 'is_active',
                   'created_at', 'updated_at'],
    '_sale_orders': ['_id', 'order_number', 'customer', 'warehouse', 'items', 'subtotal',
                     'tax_amount', 'discount_amount', 'total_amount', 'order_status', 'payment_status',
                     'notes', 'created_by', 'created_at', 'updated_at'],
    '_suppliers_legacy': ['_id', 'code', 'company_name', 'contact_name', 'email', 'phone',
                          'address', 'city', 'state', 'country', 'pin_code', 'gst_number',
                          'bank_details', 'payment_terms', 'credit_limit', 'is_active',
                          'created_at', 'updated_at'],
    '_warehouses': ['_id', 'code', 'name', 'address', 'city', 'state', 'contact_person',
                    'phone', 'locations', 'is_active', 'created_at', 'updated_at'],
    '_inventory': ['_id', 'product', 'variant', 'warehouse', 'quantity', 'reserved_quantity',
                   'available_quantity', 'cost_price', 'reorder_level', 'last_restocked',
                   'created_at', 'updated_at'],
    '_stock_movements': ['_id', 'product_id', 'variant_sku', 'warehouse_id', 'movement_type',
                         'quantity', 'reference_type', 'reference_id', 'notes', 'created_by',
                         'created_at'],
    '_transfers': ['_id', 'transfer_number', 'from_warehouse', 'to_warehouse', 'status',
                   'items', 'notes', 'created_by', 'approved_by', 'shipped_by', 'received_by',
                   'created_at', 'updated_at'],
    '_adjustments': ['_id', 'adjustment_number', 'warehouse', 'adjustment_type', 'status',
                     'items', 'reason', 'notes', 'created_by', 'approved_by',
                     'created_at', 'updated_at'],
    '_audit_log': ['_id', 'user_id', 'user_email', 'user_name', 'action', 'module',
                   'resource_type', 'resource_id', 'changes', 'context', 'created_at'],
    '_settings': ['_id', 'company_name', 'company_address', 'company_phone', 'company_email',
                  'company_gst', 'company_logo', 'invoice_prefix', 'invoice_next_number',
                  'po_prefix', 'po_next_number', 'so_prefix', 'so_next_number',
                  'transfer_prefix', 'transfer_next_number', 'adjustment_prefix', 'adjustment_next_number',
                  'default_warehouse', 'default_currency', 'tax_rate', 'updated_at'],
}


async def connect_to_sheets():
    """Initialize Google Sheets database — called on app startup."""
    db = await init_sheets_db()

    if db.demo_mode:
        logger.warning("Running in DEMO MODE — no Google Sheets connection")
        # Still set up in-memory cache with schemas
        for tab_name, headers in TAB_SCHEMAS.items():
            db.ensure_tab(tab_name, headers)
        # Seed demo data in memory so app is functional
        try:
            from .services.seed_sheets_service import seed_all_data
            await seed_all_data(db)
            logger.warning(f"Seeded {len(db.find('_users'))} users in demo mode")
        except Exception as e:
            logger.error(f"Demo seed error: {e}")
        return

    # Ensure all tabs exist with proper headers
    for tab_name, headers in TAB_SCHEMAS.items():
        try:
            db.ensure_tab(tab_name, headers)
        except Exception as e:
            logger.error(f"Failed to ensure tab {tab_name}: {e}")

    # Check if seed data needed (first run)
    users = db.find('_users')
    if not users:
        logger.info("No users found — running seed data...")
        try:
            from .services.seed_sheets_service import seed_all_data
            await seed_all_data(db)
            logger.info("Seed data completed")
        except Exception as e:
            logger.error(f"Seed data error: {e}")

    logger.info("Google Sheets database ready")


async def close_sheets_connection():
    """No persistent connection to close."""
    pass
