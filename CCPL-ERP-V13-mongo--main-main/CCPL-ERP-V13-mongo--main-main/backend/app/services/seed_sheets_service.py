"""Seed initial data into Google Sheets on first run."""
import json
import uuid
import logging
from datetime import datetime
from ..core.security import get_password_hash

logger = logging.getLogger(__name__)


def _id():
    return uuid.uuid4().hex


def _now():
    return datetime.utcnow().isoformat()


def _json(obj):
    return json.dumps(obj, default=str)


async def seed_all_data(db):
    """Seed all initial data into Google Sheets."""
    logger.info("Seeding initial data...")

    _seed_users(db)
    _seed_categories(db)
    _seed_colours(db)
    _seed_sizes(db)
    _seed_uoms(db)
    _seed_variant_groups(db)
    _seed_brands(db)
    _seed_suppliers(db)
    _seed_item_types(db)

    logger.info("Seed data complete")


def _seed_users(db):
    now = _now()
    security = _json({"failed_login_attempts": 0, "two_factor_enabled": False, "must_change_password": False})
    prefs = _json({"language": "en", "timezone": "Asia/Kolkata", "date_format": "DD/MM/YYYY", "theme": "light",
                    "notifications": {"email": True, "in_app": True, "low_stock": True, "orders": True}})

    users = [
        {"_id": _id(), "email": "admin@ccpl.com", "password_hash": get_password_hash("Admin@123"),
         "full_name": "System Admin", "phone": "+91-9999999999", "avatar": "",
         "role": _json({"name": "Super Admin", "slug": "super-admin", "level": 10}),
         "additional_permissions": "[]", "denied_permissions": "[]",
         "effective_permissions": _json(["*"]),
         "team_id": "", "team_name": "", "manager": "", "assigned_warehouses": "[]",
         "status": "active", "security": security, "sessions": "[]", "invitation": "",
         "preferences": prefs, "last_login": "", "last_active": "", "login_count": "0",
         "created_by": "", "created_at": now, "updated_at": now},
        {"_id": _id(), "email": "manager@ccpl.com", "password_hash": get_password_hash("Manager@123"),
         "full_name": "Inventory Manager", "phone": "+91-8888888888", "avatar": "",
         "role": _json({"name": "Manager", "slug": "manager", "level": 20}),
         "additional_permissions": "[]", "denied_permissions": "[]",
         "effective_permissions": _json(["inventory.view", "inventory.edit", "reports.view"]),
         "team_id": "", "team_name": "", "manager": "", "assigned_warehouses": "[]",
         "status": "active", "security": security, "sessions": "[]", "invitation": "",
         "preferences": prefs, "last_login": "", "last_active": "", "login_count": "0",
         "created_by": "", "created_at": now, "updated_at": now},
        {"_id": _id(), "email": "user@ccpl.com", "password_hash": get_password_hash("User@123"),
         "full_name": "Regular User", "phone": "+91-7777777777", "avatar": "",
         "role": _json({"name": "User", "slug": "user", "level": 30}),
         "additional_permissions": "[]", "denied_permissions": "[]",
         "effective_permissions": _json(["inventory.view", "reports.view"]),
         "team_id": "", "team_name": "", "manager": "", "assigned_warehouses": "[]",
         "status": "active", "security": security, "sessions": "[]", "invitation": "",
         "preferences": prefs, "last_login": "", "last_active": "", "login_count": "0",
         "created_by": "", "created_at": now, "updated_at": now},
    ]
    db.insert_many("_users", users)
    logger.info(f"  Seeded {len(users)} users")


def _seed_categories(db):
    now = _now()
    cats = [
        {"_id": _id(), "category_code": "APRL", "category_name": "Apparel", "description": "Clothing and garments",
         "path": "APRL", "path_name": "Apparel", "child_count": "3", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "category_code": "FABR", "category_name": "Fabric", "description": "Raw fabric materials",
         "path": "FABR", "path_name": "Fabric", "child_count": "2", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "category_code": "TRIM", "category_name": "Trims & Accessories", "description": "Buttons, zippers, labels",
         "path": "TRIM", "path_name": "Trims & Accessories", "child_count": "2", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "category_code": "PACK", "category_name": "Packaging", "description": "Packaging materials",
         "path": "PACK", "path_name": "Packaging", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
    ]
    db.insert_many("_categories", cats)

    sub_cats = [
        {"_id": _id(), "sub_category_code": "MENS", "sub_category_name": "Men's Wear", "category_code": "APRL",
         "category_name": "Apparel", "description": "Men's clothing", "path": "APRL/MENS",
         "path_name": "Apparel > Men's Wear", "child_count": "2", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_category_code": "WMNS", "sub_category_name": "Women's Wear", "category_code": "APRL",
         "category_name": "Apparel", "description": "Women's clothing", "path": "APRL/WMNS",
         "path_name": "Apparel > Women's Wear", "child_count": "2", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_category_code": "KIDS", "sub_category_name": "Kids Wear", "category_code": "APRL",
         "category_name": "Apparel", "description": "Kids clothing", "path": "APRL/KIDS",
         "path_name": "Apparel > Kids Wear", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_category_code": "WOVN", "sub_category_name": "Woven Fabric", "category_code": "FABR",
         "category_name": "Fabric", "description": "Woven fabrics", "path": "FABR/WOVN",
         "path_name": "Fabric > Woven Fabric", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_category_code": "KNIT", "sub_category_name": "Knit Fabric", "category_code": "FABR",
         "category_name": "Fabric", "description": "Knitted fabrics", "path": "FABR/KNIT",
         "path_name": "Fabric > Knit Fabric", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_category_code": "BTNS", "sub_category_name": "Buttons", "category_code": "TRIM",
         "category_name": "Trims & Accessories", "description": "Buttons", "path": "TRIM/BTNS",
         "path_name": "Trims > Buttons", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_category_code": "ZIPS", "sub_category_name": "Zippers", "category_code": "TRIM",
         "category_name": "Trims & Accessories", "description": "Zippers", "path": "TRIM/ZIPS",
         "path_name": "Trims > Zippers", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
    ]
    db.insert_many("_sub_categories", sub_cats)

    divisions = [
        {"_id": _id(), "division_code": "TOPW", "division_name": "Topwear", "sub_category_code": "MENS",
         "sub_category_name": "Men's Wear", "description": "Tops, shirts, t-shirts", "path": "APRL/MENS/TOPW",
         "path_name": "Apparel > Men's Wear > Topwear", "child_count": "3", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "division_code": "BTMW", "division_name": "Bottomwear", "sub_category_code": "MENS",
         "sub_category_name": "Men's Wear", "description": "Pants, jeans", "path": "APRL/MENS/BTMW",
         "path_name": "Apparel > Men's Wear > Bottomwear", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "division_code": "DRSS", "division_name": "Dresses", "sub_category_code": "WMNS",
         "sub_category_name": "Women's Wear", "description": "Dresses", "path": "APRL/WMNS/DRSS",
         "path_name": "Apparel > Women's Wear > Dresses", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "division_code": "ETHN", "division_name": "Ethnic Wear", "sub_category_code": "WMNS",
         "sub_category_name": "Women's Wear", "description": "Traditional wear", "path": "APRL/WMNS/ETHN",
         "path_name": "Apparel > Women's Wear > Ethnic Wear", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
    ]
    db.insert_many("_divisions", divisions)

    classes = [
        {"_id": _id(), "class_code": "TSHT", "class_name": "T-Shirts", "division_code": "TOPW",
         "division_name": "Topwear", "description": "T-shirts", "path": "APRL/MENS/TOPW/TSHT",
         "path_name": "Topwear > T-Shirts", "child_count": "3", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "class_code": "SHRT", "class_name": "Shirts", "division_code": "TOPW",
         "division_name": "Topwear", "description": "Formal/casual shirts", "path": "APRL/MENS/TOPW/SHRT",
         "path_name": "Topwear > Shirts", "child_count": "2", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
        {"_id": _id(), "class_code": "JEAN", "class_name": "Jeans", "division_code": "BTMW",
         "division_name": "Bottomwear", "description": "Denim jeans", "path": "APRL/MENS/BTMW/JEAN",
         "path_name": "Bottomwear > Jeans", "child_count": "0", "is_active": "True", "deleted_at": "",
         "created_at": now, "updated_at": now},
    ]
    db.insert_many("_classes", classes)

    sub_classes = [
        {"_id": _id(), "sub_class_code": "RNCK", "sub_class_name": "Round Neck", "class_code": "TSHT",
         "class_name": "T-Shirts", "description": "Round neck t-shirts", "path": "APRL/MENS/TOPW/TSHT/RNCK",
         "path_name": "T-Shirts > Round Neck", "is_active": "True", "deleted_at": "", "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_class_code": "VNCK", "sub_class_name": "V-Neck", "class_code": "TSHT",
         "class_name": "T-Shirts", "description": "V-neck t-shirts", "path": "APRL/MENS/TOPW/TSHT/VNCK",
         "path_name": "T-Shirts > V-Neck", "is_active": "True", "deleted_at": "", "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_class_code": "POLO", "sub_class_name": "Polo", "class_code": "TSHT",
         "class_name": "T-Shirts", "description": "Polo t-shirts", "path": "APRL/MENS/TOPW/TSHT/POLO",
         "path_name": "T-Shirts > Polo", "is_active": "True", "deleted_at": "", "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_class_code": "FRML", "sub_class_name": "Formal", "class_code": "SHRT",
         "class_name": "Shirts", "description": "Formal shirts", "path": "APRL/MENS/TOPW/SHRT/FRML",
         "path_name": "Shirts > Formal", "is_active": "True", "deleted_at": "", "created_at": now, "updated_at": now},
        {"_id": _id(), "sub_class_code": "CASL", "sub_class_name": "Casual", "class_code": "SHRT",
         "class_name": "Shirts", "description": "Casual shirts", "path": "APRL/MENS/TOPW/SHRT/CASL",
         "path_name": "Shirts > Casual", "is_active": "True", "deleted_at": "", "created_at": now, "updated_at": now},
    ]
    db.insert_many("_sub_classes", sub_classes)
    logger.info("  Seeded categories (4 + 7 + 4 + 3 + 5)")


def _seed_colours(db):
    now = _now()
    colours = [
        ("BLK", "Black", "#000000"), ("WHT", "White", "#FFFFFF"), ("NVY", "Navy Blue", "#000080"),
        ("RED", "Red", "#FF0000"), ("GRN", "Green", "#008000"), ("BLU", "Blue", "#0000FF"),
        ("GRY", "Grey", "#808080"), ("YLW", "Yellow", "#FFFF00"), ("ORG", "Orange", "#FFA500"),
        ("PNK", "Pink", "#FFC0CB"), ("PRP", "Purple", "#800080"), ("BRN", "Brown", "#8B4513"),
        ("BGE", "Beige", "#F5F5DC"), ("MAR", "Maroon", "#800000"), ("TEA", "Teal", "#008080"),
    ]
    rows = [{"_id": _id(), "colour_code": c, "colour_name": n, "colour_hex": h, "rgb_value": "",
             "colour_group": "BASIC", "group_name": "Basic Colors", "is_active": "True", "deleted_at": "",
             "created_at": now, "updated_at": now} for c, n, h in colours]
    db.insert_many("_colour_master", rows)
    logger.info(f"  Seeded {len(rows)} colours")


def _seed_sizes(db):
    now = _now()
    sizes = [
        ("XS", "Extra Small", "ALPHA", 1), ("S", "Small", "ALPHA", 2), ("M", "Medium", "ALPHA", 3),
        ("L", "Large", "ALPHA", 4), ("XL", "Extra Large", "ALPHA", 5), ("XXL", "2X Large", "ALPHA", 6),
        ("3XL", "3X Large", "ALPHA", 7),
        ("28", "28", "NUMERIC", 28), ("30", "30", "NUMERIC", 30), ("32", "32", "NUMERIC", 32),
        ("34", "34", "NUMERIC", 34), ("36", "36", "NUMERIC", 36), ("38", "38", "NUMERIC", 38),
        ("40", "40", "NUMERIC", 40),
    ]
    rows = [{"_id": _id(), "size_code": c, "size_name": n, "size_group": g, "group_name": g + " Sizes",
             "numeric_value": str(v), "sort_order": str(v), "is_active": "True", "deleted_at": "",
             "created_at": now, "updated_at": now} for c, n, g, v in sizes]
    db.insert_many("_size_master", rows)
    logger.info(f"  Seeded {len(rows)} sizes")


def _seed_uoms(db):
    now = _now()
    uoms = [
        ("PCS", "Pieces", "PCS", "COUNT", 1, True), ("DOZ", "Dozen", "DOZ", "COUNT", 12, False),
        ("GRS", "Gross", "GRS", "COUNT", 144, False), ("SET", "Set", "SET", "COUNT", 1, True),
        ("PAR", "Pair", "PAR", "COUNT", 2, False),
        ("MTR", "Meters", "m", "LENGTH", 1, True), ("CM", "Centimeters", "cm", "LENGTH", 0.01, False),
        ("YRD", "Yards", "yd", "LENGTH", 0.9144, False), ("IN", "Inches", "in", "LENGTH", 0.0254, False),
        ("KG", "Kilograms", "kg", "WEIGHT", 1, True), ("GM", "Grams", "g", "WEIGHT", 0.001, False),
        ("LB", "Pounds", "lb", "WEIGHT", 0.4536, False),
        ("SQM", "Square Meters", "sqm", "AREA", 1, True), ("SQFT", "Square Feet", "sqft", "AREA", 0.0929, False),
    ]
    rows = [{"_id": _id(), "uom_code": c, "uom_name": n, "uom_symbol": s, "uom_group": g,
             "group_name": g, "conversion_to_base": str(conv), "is_base_uom": str(base),
             "is_active": "True", "deleted_at": "", "created_at": now, "updated_at": now}
            for c, n, s, g, conv, base in uoms]
    db.insert_many("_uom_master", rows)
    logger.info(f"  Seeded {len(rows)} UOMs")


def _seed_variant_groups(db):
    now = _now()
    groups = [
        ("COLOUR", "BASIC", "Basic Colors", 1), ("COLOUR", "PASTEL", "Pastel Colors", 2),
        ("COLOUR", "NEON", "Neon Colors", 3), ("COLOUR", "NEUTRAL", "Neutral Colors", 4),
        ("COLOUR", "DENIM", "Denim Shades", 5),
        ("SIZE", "ALPHA", "Alpha Sizes", 1), ("SIZE", "NUMERIC", "Numeric Sizes", 2),
        ("SIZE", "AGE", "Age-based Sizes", 3), ("SIZE", "SHOE", "Shoe Sizes", 4),
        ("SIZE", "RING", "Ring Sizes", 5),
        ("UOM", "COUNT", "Counting Units", 1), ("UOM", "LENGTH", "Length Units", 2),
        ("UOM", "WEIGHT", "Weight Units", 3), ("UOM", "AREA", "Area Units", 4),
        ("UOM", "VOLUME", "Volume Units", 5),
    ]
    rows = [{"_id": _id(), "variant_type": t, "group_code": c, "group_name": n,
             "description": "", "sort_order": str(s), "is_active": "True",
             "created_at": now, "updated_at": now} for t, c, n, s in groups]
    db.insert_many("_variant_groups", rows)
    logger.info(f"  Seeded {len(rows)} variant groups")


def _seed_brands(db):
    now = _now()
    brands = [
        ("BR-001", "Confidence Clothing", "In-house"), ("BR-002", "Premium Line", "Premium"),
        ("BR-003", "Urban Edge", "Casual"), ("BR-004", "Classic Fit", "Formal"),
        ("BR-005", "Active Wear", "Sports"),
    ]
    rows = [{"_id": _id(), "brand_code": c, "brand_name": n, "brand_category": cat,
             "description": "", "logo_url": "", "is_active": "True", "deleted_at": "",
             "created_by": "", "created_at": now, "updated_at": now} for c, n, cat in brands]
    db.insert_many("_brand_master", rows)
    logger.info(f"  Seeded {len(rows)} brands")


def _seed_suppliers(db):
    now = _now()
    suppliers = [
        ("SUP-001", "Fabric World Textiles", "Manufacturer", "Mumbai"),
        ("SUP-002", "Global Trims Co.", "Wholesaler", "Delhi"),
        ("SUP-003", "Quality Threads Ltd.", "Manufacturer", "Surat"),
        ("SUP-004", "Eastern Dyes & Chemicals", "Distributor", "Ahmedabad"),
        ("SUP-005", "Premium Packaging", "Wholesaler", "Kolkata"),
    ]
    rows = [{"_id": _id(), "supplier_code": c, "supplier_name": n, "supplier_type": t,
             "contact_person": "", "email": "", "phone": "", "address": "", "city": city,
             "state": "", "country": "India", "pin_code": "", "gst_number": "", "pan_number": "",
             "payment_terms": "Net 30", "credit_limit": "100000", "bank_details": "",
             "is_active": "True", "deleted_at": "", "created_by": "", "created_at": now, "updated_at": now}
            for c, n, t, city in suppliers]
    db.insert_many("_supplier_master", rows)
    logger.info(f"  Seeded {len(rows)} suppliers")


def _seed_item_types(db):
    now = _now()
    types = [
        ("YN", "Yarn & Fiber", True, False, True), ("GF", "Greige Fabric", True, False, True),
        ("DF", "Dyed Fabric", True, False, True), ("TR", "Trims & Accessories", True, False, True),
        ("DY", "Dyes & Chemicals", True, False, True), ("CP", "Cut Panels", False, False, True),
        ("SF", "Semi Finished", False, False, True), ("FG", "Finished Goods", False, True, True),
        ("PK", "Packaging", True, False, True), ("CS", "Consumables", True, False, False),
    ]
    rows = [{"_id": _id(), "type_code": c, "type_name": n, "description": "",
             "allow_purchase": str(p), "allow_sale": str(s), "track_inventory": str(inv),
             "require_quality_check": "False", "default_uom": "PCS", "color_code": "", "icon": "",
             "sort_order": str(i + 1), "is_active": "True", "created_by": "", "updated_by": "",
             "created_at": now, "updated_at": now}
            for i, (c, n, p, s, inv) in enumerate(types)]
    db.insert_many("_item_types", rows)
    logger.info(f"  Seeded {len(rows)} item types")
