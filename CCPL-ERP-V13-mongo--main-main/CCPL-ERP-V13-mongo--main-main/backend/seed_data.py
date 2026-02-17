"""
Comprehensive Seed Data Script for MongoDB Atlas
Creates demo users, categories, brands, suppliers, colors, sizes, UOMs
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import bcrypt

# MongoDB Atlas Connection
MONGODB_URL = "mongodb+srv://tech_db_user:Tech3112@cluster0.empai1t.mongodb.net/?appName=Cluster0"
DATABASE_NAME = "inventory_erp"


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


async def seed_database():
    """Main seed function"""
    print("🚀 Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        
        # ==================== SEED USERS ====================
        print("\n📦 Seeding Users...")
        users_collection = db["users"]
        
        # Clear existing users (optional - comment out if you want to keep)
        await users_collection.delete_many({})
        
        users = [
            {
                "email": "admin@ccpl.com",
                "password_hash": hash_password("Admin@123"),
                "full_name": "System Admin",
                "phone": "+91-9999999999",
                "role": {
                    "name": "Super Admin",
                    "slug": "super-admin",
                    "level": 10
                },
                "status": "active",
                "effective_permissions": ["*"],
                "additional_permissions": [],
                "denied_permissions": [],
                "assigned_warehouses": [],
                "sessions": [],
                "security": {
                    "failed_login_attempts": 0,
                    "two_factor_enabled": False,
                    "must_change_password": False
                },
                "preferences": {
                    "language": "en",
                    "timezone": "Asia/Kolkata",
                    "date_format": "DD/MM/YYYY",
                    "theme": "light",
                    "notifications": {"email": True, "in_app": True, "low_stock": True, "orders": True}
                },
                "login_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "email": "manager@ccpl.com",
                "password_hash": hash_password("Manager@123"),
                "full_name": "Inventory Manager",
                "phone": "+91-8888888888",
                "role": {
                    "name": "Manager",
                    "slug": "manager",
                    "level": 20
                },
                "status": "active",
                "effective_permissions": ["inventory.view", "inventory.edit", "reports.view"],
                "additional_permissions": [],
                "denied_permissions": [],
                "assigned_warehouses": [],
                "sessions": [],
                "security": {
                    "failed_login_attempts": 0,
                    "two_factor_enabled": False,
                    "must_change_password": False
                },
                "preferences": {
                    "language": "en",
                    "timezone": "Asia/Kolkata",
                    "date_format": "DD/MM/YYYY",
                    "theme": "light",
                    "notifications": {"email": True, "in_app": True, "low_stock": True, "orders": True}
                },
                "login_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "email": "user@ccpl.com",
                "password_hash": hash_password("User@123"),
                "full_name": "Regular User",
                "phone": "+91-7777777777",
                "role": {
                    "name": "User",
                    "slug": "user",
                    "level": 30
                },
                "status": "active",
                "effective_permissions": ["inventory.view", "reports.view"],
                "additional_permissions": [],
                "denied_permissions": [],
                "assigned_warehouses": [],
                "sessions": [],
                "security": {
                    "failed_login_attempts": 0,
                    "two_factor_enabled": False,
                    "must_change_password": False
                },
                "preferences": {
                    "language": "en",
                    "timezone": "Asia/Kolkata",
                    "date_format": "DD/MM/YYYY",
                    "theme": "light",
                    "notifications": {"email": True, "in_app": True, "low_stock": True, "orders": True}
                },
                "login_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await users_collection.insert_many(users)
        print(f"   ✅ Created {len(result.inserted_ids)} users")
        
        # ==================== SEED ITEM CATEGORIES (Level 1) ====================
        print("\n📦 Seeding Item Categories (Level 1)...")
        categories_collection = db["item_categories"]
        await categories_collection.delete_many({})
        
        categories = [
            {
                "category_code": "APRL",
                "category_name": "Apparel",
                "description": "Clothing and garments",
                "item_type": "FG",
                "level_names": {"l1": "Category", "l2": "Gender", "l3": "Type", "l4": "Style", "l5": "Variant"},
                "has_color": True,
                "has_size": True,
                "has_fabric": True,
                "has_brand": True,
                "has_style": True,
                "has_season": True,
                "default_hsn_code": "6109",
                "default_gst_rate": 5.0,
                "default_uom": "PCS",
                "icon": "Shirt",
                "color_code": "#10b981",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 3,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "category_code": "FABR",
                "category_name": "Fabric",
                "description": "Raw fabric materials",
                "item_type": "RM",
                "level_names": {"l1": "Category", "l2": "Type", "l3": "Composition", "l4": "Weight", "l5": "Finish"},
                "has_color": True,
                "has_size": False,
                "has_fabric": True,
                "has_brand": True,
                "has_style": False,
                "has_season": False,
                "default_hsn_code": "5208",
                "default_gst_rate": 5.0,
                "default_uom": "MTR",
                "icon": "Layers",
                "color_code": "#3b82f6",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "category_code": "TRIM",
                "category_name": "Trims & Accessories",
                "description": "Buttons, zippers, labels, etc.",
                "item_type": "RM",
                "level_names": {"l1": "Category", "l2": "Type", "l3": "Material", "l4": "Size", "l5": "Finish"},
                "has_color": True,
                "has_size": True,
                "has_fabric": False,
                "has_brand": True,
                "has_style": False,
                "has_season": False,
                "default_hsn_code": "9606",
                "default_gst_rate": 18.0,
                "default_uom": "PCS",
                "icon": "Puzzle",
                "color_code": "#8b5cf6",
                "sort_order": 3,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "category_code": "PACK",
                "category_name": "Packaging",
                "description": "Packaging materials",
                "item_type": "RM",
                "level_names": {"l1": "Category", "l2": "Type", "l3": "Material", "l4": "Size", "l5": "Style"},
                "has_color": False,
                "has_size": True,
                "has_fabric": False,
                "has_brand": False,
                "has_style": False,
                "has_season": False,
                "default_hsn_code": "4819",
                "default_gst_rate": 18.0,
                "default_uom": "PCS",
                "icon": "Package",
                "color_code": "#f59e0b",
                "sort_order": 4,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await categories_collection.insert_many(categories)
        print(f"   ✅ Created {len(result.inserted_ids)} categories")
        
        # ==================== SEED SUB-CATEGORIES (Level 2) ====================
        print("\n📦 Seeding Sub-Categories (Level 2)...")
        sub_categories_collection = db["item_sub_categories"]
        await sub_categories_collection.delete_many({})
        
        sub_categories = [
            # Apparel Sub-Categories
            {
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "description": "Men's clothing",
                "category_code": "APRL",
                "category_name": "Apparel",
                "path": "APRL/MENS",
                "path_name": "Apparel > Men's Wear",
                "item_type": "FG",
                "icon": "User",
                "color_code": "#3b82f6",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_category_code": "WMNS",
                "sub_category_name": "Women's Wear",
                "description": "Women's clothing",
                "category_code": "APRL",
                "category_name": "Apparel",
                "path": "APRL/WMNS",
                "path_name": "Apparel > Women's Wear",
                "item_type": "FG",
                "icon": "User",
                "color_code": "#ec4899",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_category_code": "KIDS",
                "sub_category_name": "Kids Wear",
                "description": "Children's clothing",
                "category_code": "APRL",
                "category_name": "Apparel",
                "path": "APRL/KIDS",
                "path_name": "Apparel > Kids Wear",
                "item_type": "FG",
                "icon": "Baby",
                "color_code": "#f59e0b",
                "sort_order": 3,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            # Fabric Sub-Categories
            {
                "sub_category_code": "WOVN",
                "sub_category_name": "Woven",
                "description": "Woven fabrics",
                "category_code": "FABR",
                "category_name": "Fabric",
                "path": "FABR/WOVN",
                "path_name": "Fabric > Woven",
                "item_type": "RM",
                "icon": "Grid",
                "color_code": "#6366f1",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_category_code": "KNIT",
                "sub_category_name": "Knit",
                "description": "Knitted fabrics",
                "category_code": "FABR",
                "category_name": "Fabric",
                "path": "FABR/KNIT",
                "path_name": "Fabric > Knit",
                "item_type": "RM",
                "icon": "Link",
                "color_code": "#14b8a6",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            # Trim Sub-Categories
            {
                "sub_category_code": "BTNS",
                "sub_category_name": "Buttons",
                "description": "All types of buttons",
                "category_code": "TRIM",
                "category_name": "Trims & Accessories",
                "path": "TRIM/BTNS",
                "path_name": "Trims > Buttons",
                "item_type": "RM",
                "icon": "Circle",
                "color_code": "#8b5cf6",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_category_code": "ZIPS",
                "sub_category_name": "Zippers",
                "description": "All types of zippers",
                "category_code": "TRIM",
                "category_name": "Trims & Accessories",
                "path": "TRIM/ZIPS",
                "path_name": "Trims > Zippers",
                "item_type": "RM",
                "icon": "ArrowUp",
                "color_code": "#f97316",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await sub_categories_collection.insert_many(sub_categories)
        print(f"   ✅ Created {len(result.inserted_ids)} sub-categories")
        
        # ==================== SEED DIVISIONS (Level 3) ====================
        print("\n📦 Seeding Divisions (Level 3)...")
        divisions_collection = db["item_divisions"]
        await divisions_collection.delete_many({})
        
        divisions = [
            {
                "division_code": "TOPW",
                "division_name": "Topwear",
                "description": "Upper body garments",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "path": "APRL/MENS/TOPW",
                "path_name": "Apparel > Men's Wear > Topwear",
                "item_type": "FG",
                "icon": "Shirt",
                "color_code": "#3b82f6",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "division_code": "BTMW",
                "division_name": "Bottomwear",
                "description": "Lower body garments",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "path": "APRL/MENS/BTMW",
                "path_name": "Apparel > Men's Wear > Bottomwear",
                "item_type": "FG",
                "icon": "PanelBottom",
                "color_code": "#6366f1",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 1,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "division_code": "DRSS",
                "division_name": "Dresses",
                "description": "Dresses and gowns",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "WMNS",
                "sub_category_name": "Women's Wear",
                "path": "APRL/WMNS/DRSS",
                "path_name": "Apparel > Women's Wear > Dresses",
                "item_type": "FG",
                "icon": "Shirt",
                "color_code": "#ec4899",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "division_code": "ETHN",
                "division_name": "Ethnic Wear",
                "description": "Traditional and ethnic clothing",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "WMNS",
                "sub_category_name": "Women's Wear",
                "path": "APRL/WMNS/ETHN",
                "path_name": "Apparel > Women's Wear > Ethnic Wear",
                "item_type": "FG",
                "icon": "Star",
                "color_code": "#f59e0b",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await divisions_collection.insert_many(divisions)
        print(f"   ✅ Created {len(result.inserted_ids)} divisions")
        
        # ==================== SEED CLASSES (Level 4) ====================
        print("\n📦 Seeding Classes (Level 4)...")
        classes_collection = db["item_classes"]
        await classes_collection.delete_many({})
        
        classes = [
            {
                "class_code": "TSHT",
                "class_name": "T-Shirts",
                "description": "T-Shirts and casual tops",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "TOPW",
                "division_name": "Topwear",
                "path": "APRL/MENS/TOPW/TSHT",
                "path_name": "Apparel > Men > Topwear > T-Shirts",
                "item_type": "FG",
                "icon": "Shirt",
                "color_code": "#3b82f6",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 3,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "class_code": "SHRT",
                "class_name": "Shirts",
                "description": "Formal and casual shirts",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "TOPW",
                "division_name": "Topwear",
                "path": "APRL/MENS/TOPW/SHRT",
                "path_name": "Apparel > Men > Topwear > Shirts",
                "item_type": "FG",
                "icon": "Shirt",
                "color_code": "#6366f1",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "class_code": "JEAN",
                "class_name": "Jeans",
                "description": "Denim jeans",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "BTMW",
                "division_name": "Bottomwear",
                "path": "APRL/MENS/BTMW/JEAN",
                "path_name": "Apparel > Men > Bottomwear > Jeans",
                "item_type": "FG",
                "icon": "PanelBottom",
                "color_code": "#14b8a6",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "child_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await classes_collection.insert_many(classes)
        print(f"   ✅ Created {len(result.inserted_ids)} classes")
        
        # ==================== SEED SUB-CLASSES (Level 5) ====================
        print("\n📦 Seeding Sub-Classes (Level 5)...")
        sub_classes_collection = db["item_sub_classes"]
        await sub_classes_collection.delete_many({})
        
        sub_classes = [
            {
                "sub_class_code": "RNCK",
                "sub_class_name": "Round Neck",
                "description": "Round neck t-shirts",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "TOPW",
                "division_name": "Topwear",
                "class_code": "TSHT",
                "class_name": "T-Shirts",
                "path": "APRL/MENS/TOPW/TSHT/RNCK",
                "path_name": "Apparel > Men > Topwear > T-Shirts > Round Neck",
                "item_type": "FG",
                "icon": "Circle",
                "color_code": "#3b82f6",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_class_code": "VNCK",
                "sub_class_name": "V-Neck",
                "description": "V-neck t-shirts",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "TOPW",
                "division_name": "Topwear",
                "class_code": "TSHT",
                "class_name": "T-Shirts",
                "path": "APRL/MENS/TOPW/TSHT/VNCK",
                "path_name": "Apparel > Men > Topwear > T-Shirts > V-Neck",
                "item_type": "FG",
                "icon": "ChevronDown",
                "color_code": "#6366f1",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_class_code": "POLO",
                "sub_class_name": "Polo",
                "description": "Polo t-shirts with collar",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "TOPW",
                "division_name": "Topwear",
                "class_code": "TSHT",
                "class_name": "T-Shirts",
                "path": "APRL/MENS/TOPW/TSHT/POLO",
                "path_name": "Apparel > Men > Topwear > T-Shirts > Polo",
                "item_type": "FG",
                "icon": "Tag",
                "color_code": "#14b8a6",
                "sort_order": 3,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_class_code": "FRML",
                "sub_class_name": "Formal",
                "description": "Formal shirts",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "TOPW",
                "division_name": "Topwear",
                "class_code": "SHRT",
                "class_name": "Shirts",
                "path": "APRL/MENS/TOPW/SHRT/FRML",
                "path_name": "Apparel > Men > Topwear > Shirts > Formal",
                "item_type": "FG",
                "icon": "Briefcase",
                "color_code": "#1f2937",
                "sort_order": 1,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "sub_class_code": "CASL",
                "sub_class_name": "Casual",
                "description": "Casual shirts",
                "category_code": "APRL",
                "category_name": "Apparel",
                "sub_category_code": "MENS",
                "sub_category_name": "Men's Wear",
                "division_code": "TOPW",
                "division_name": "Topwear",
                "class_code": "SHRT",
                "class_name": "Shirts",
                "path": "APRL/MENS/TOPW/SHRT/CASL",
                "path_name": "Apparel > Men > Topwear > Shirts > Casual",
                "item_type": "FG",
                "icon": "Sun",
                "color_code": "#f59e0b",
                "sort_order": 2,
                "status": "active",
                "is_active": True,
                "is_deleted": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await sub_classes_collection.insert_many(sub_classes)
        print(f"   ✅ Created {len(result.inserted_ids)} sub-classes")
        
        # ==================== SEED BRANDS ====================
        print("\n📦 Seeding Brands...")
        brands_collection = db["brand_master"]
        await brands_collection.delete_many({})
        
        brands = [
            {
                "brand_code": "BR-001",
                "brand_name": "CCPL Premium",
                "brand_category": "Apparel",
                "country": "India",
                "contact_person": "Rahul Sharma",
                "email": "rahul@ccpl.com",
                "phone": "+91-9876543210",
                "website": "www.ccpl.com",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "brand_code": "BR-002",
                "brand_name": "Urban Style",
                "brand_category": "Casual Wear",
                "country": "India",
                "contact_person": "Priya Patel",
                "email": "priya@urbanstyle.com",
                "phone": "+91-9876543211",
                "website": "www.urbanstyle.com",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "brand_code": "BR-003",
                "brand_name": "Classic Cottons",
                "brand_category": "Fabric",
                "country": "India",
                "contact_person": "Amit Kumar",
                "email": "amit@classiccottons.com",
                "phone": "+91-9876543212",
                "website": "www.classiccottons.com",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "brand_code": "BR-004",
                "brand_name": "Trendy Trims",
                "brand_category": "Trims",
                "country": "China",
                "contact_person": "Li Wei",
                "email": "liwei@trendytrims.cn",
                "phone": "+86-13912345678",
                "website": "www.trendytrims.cn",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "brand_code": "BR-005",
                "brand_name": "Eco Fabrics",
                "brand_category": "Sustainable Fabric",
                "country": "India",
                "contact_person": "Neha Singh",
                "email": "neha@ecofabrics.in",
                "phone": "+91-9876543213",
                "website": "www.ecofabrics.in",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await brands_collection.insert_many(brands)
        print(f"   ✅ Created {len(result.inserted_ids)} brands")
        
        # ==================== SEED SUPPLIERS ====================
        print("\n📦 Seeding Suppliers...")
        suppliers_collection = db["supplier_master"]
        await suppliers_collection.delete_many({})
        
        suppliers = [
            {
                "supplier_code": "SUP-001",
                "supplier_name": "Delhi Textiles Pvt Ltd",
                "supplier_type": "Fabric Supplier",
                "country": "India",
                "city": "Delhi",
                "contact_person": "Rajesh Gupta",
                "email": "rajesh@delhitextiles.com",
                "phone": "+91-9111111111",
                "address": "123 Textile Market, Chandni Chowk, Delhi",
                "gst_number": "07AABCT1234H1Z5",
                "payment_terms": "Net 30",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "supplier_code": "SUP-002",
                "supplier_name": "Mumbai Buttons & Trims",
                "supplier_type": "Trim Supplier",
                "country": "India",
                "city": "Mumbai",
                "contact_person": "Suresh Patel",
                "email": "suresh@mumbaitrims.com",
                "phone": "+91-9222222222",
                "address": "456 Fashion Street, Mumbai",
                "gst_number": "27AABCT5678H1Z5",
                "payment_terms": "Advance",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "supplier_code": "SUP-003",
                "supplier_name": "Tirupur Garments Co",
                "supplier_type": "Garment Manufacturer",
                "country": "India",
                "city": "Tirupur",
                "contact_person": "Karthik Raman",
                "email": "karthik@tirupurgarments.com",
                "phone": "+91-9333333333",
                "address": "789 Industrial Area, Tirupur",
                "gst_number": "33AABCT9012H1Z5",
                "payment_terms": "Net 45",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "supplier_code": "SUP-004",
                "supplier_name": "Surat Silk Mills",
                "supplier_type": "Silk Supplier",
                "country": "India",
                "city": "Surat",
                "contact_person": "Hemant Shah",
                "email": "hemant@suratsilk.com",
                "phone": "+91-9444444444",
                "address": "101 Silk Market, Ring Road, Surat",
                "gst_number": "24AABCT3456H1Z5",
                "payment_terms": "Net 30",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "supplier_code": "SUP-005",
                "supplier_name": "China Zipper Co Ltd",
                "supplier_type": "Zipper Supplier",
                "country": "China",
                "city": "Guangzhou",
                "contact_person": "Zhang Wei",
                "email": "zhang@chinazipper.cn",
                "phone": "+86-13800138000",
                "address": "Building A, Industrial Zone, Guangzhou",
                "gst_number": None,
                "payment_terms": "LC at Sight",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        result = await suppliers_collection.insert_many(suppliers)
        print(f"   ✅ Created {len(result.inserted_ids)} suppliers")
        
        # ==================== SEED COLOURS ====================
        print("\n📦 Seeding Colours...")
        colours_collection = db["colour_master"]
        await colours_collection.delete_many({})
        
        colours = [
            {"colour_code": "BLK", "colour_name": "Black", "colour_hex": "#000000", "rgb_value": {"r": 0, "g": 0, "b": 0}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 1, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "WHT", "colour_name": "White", "colour_hex": "#FFFFFF", "rgb_value": {"r": 255, "g": 255, "b": 255}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 2, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "NVY", "colour_name": "Navy Blue", "colour_hex": "#000080", "rgb_value": {"r": 0, "g": 0, "b": 128}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 3, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "RED", "colour_name": "Red", "colour_hex": "#FF0000", "rgb_value": {"r": 255, "g": 0, "b": 0}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 4, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "GRN", "colour_name": "Green", "colour_hex": "#008000", "rgb_value": {"r": 0, "g": 128, "b": 0}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 5, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "BLU", "colour_name": "Blue", "colour_hex": "#0000FF", "rgb_value": {"r": 0, "g": 0, "b": 255}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 6, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "GRY", "colour_name": "Grey", "colour_hex": "#808080", "rgb_value": {"r": 128, "g": 128, "b": 128}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 7, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "YLW", "colour_name": "Yellow", "colour_hex": "#FFFF00", "rgb_value": {"r": 255, "g": 255, "b": 0}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 8, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "ORG", "colour_name": "Orange", "colour_hex": "#FFA500", "rgb_value": {"r": 255, "g": 165, "b": 0}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 9, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "PNK", "colour_name": "Pink", "colour_hex": "#FFC0CB", "rgb_value": {"r": 255, "g": 192, "b": 203}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 10, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "PRP", "colour_name": "Purple", "colour_hex": "#800080", "rgb_value": {"r": 128, "g": 0, "b": 128}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 11, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "BRN", "colour_name": "Brown", "colour_hex": "#A52A2A", "rgb_value": {"r": 165, "g": 42, "b": 42}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 12, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "BGE", "colour_name": "Beige", "colour_hex": "#F5F5DC", "rgb_value": {"r": 245, "g": 245, "b": 220}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 13, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "MAR", "colour_name": "Maroon", "colour_hex": "#800000", "rgb_value": {"r": 128, "g": 0, "b": 0}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 14, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"colour_code": "TEA", "colour_name": "Teal", "colour_hex": "#008080", "rgb_value": {"r": 0, "g": 128, "b": 128}, "colour_group": "FABRIC_COLORS", "group_name": "Fabric Colors", "is_active": True, "display_order": 15, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
        ]
        
        result = await colours_collection.insert_many(colours)
        print(f"   ✅ Created {len(result.inserted_ids)} colours")
        
        # ==================== SEED SIZES ====================
        print("\n📦 Seeding Sizes...")
        sizes_collection = db["size_master"]
        await sizes_collection.delete_many({})
        
        sizes = [
            # Apparel Sizes
            {"size_code": "XS", "size_name": "Extra Small", "size_group": "APPAREL_SIZES", "group_name": "Apparel Sizes", "unit": "SIZE", "is_active": True, "display_order": 1, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "S", "size_name": "Small", "size_group": "APPAREL_SIZES", "group_name": "Apparel Sizes", "unit": "SIZE", "is_active": True, "display_order": 2, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "M", "size_name": "Medium", "size_group": "APPAREL_SIZES", "group_name": "Apparel Sizes", "unit": "SIZE", "is_active": True, "display_order": 3, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "L", "size_name": "Large", "size_group": "APPAREL_SIZES", "group_name": "Apparel Sizes", "unit": "SIZE", "is_active": True, "display_order": 4, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "XL", "size_name": "Extra Large", "size_group": "APPAREL_SIZES", "group_name": "Apparel Sizes", "unit": "SIZE", "is_active": True, "display_order": 5, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "XXL", "size_name": "Double Extra Large", "size_group": "APPAREL_SIZES", "group_name": "Apparel Sizes", "unit": "SIZE", "is_active": True, "display_order": 6, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "3XL", "size_name": "Triple Extra Large", "size_group": "APPAREL_SIZES", "group_name": "Apparel Sizes", "unit": "SIZE", "is_active": True, "display_order": 7, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            # Numeric Sizes
            {"size_code": "28", "size_name": "28", "size_group": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "numeric_value": 28, "unit": "INCH", "is_active": True, "display_order": 1, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "30", "size_name": "30", "size_group": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "numeric_value": 30, "unit": "INCH", "is_active": True, "display_order": 2, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "32", "size_name": "32", "size_group": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "numeric_value": 32, "unit": "INCH", "is_active": True, "display_order": 3, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "34", "size_name": "34", "size_group": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "numeric_value": 34, "unit": "INCH", "is_active": True, "display_order": 4, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "36", "size_name": "36", "size_group": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "numeric_value": 36, "unit": "INCH", "is_active": True, "display_order": 5, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "38", "size_name": "38", "size_group": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "numeric_value": 38, "unit": "INCH", "is_active": True, "display_order": 6, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"size_code": "40", "size_name": "40", "size_group": "NUMERIC_SIZES", "group_name": "Numeric Sizes", "numeric_value": 40, "unit": "INCH", "is_active": True, "display_order": 7, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
        ]
        
        result = await sizes_collection.insert_many(sizes)
        print(f"   ✅ Created {len(result.inserted_ids)} sizes")
        
        # ==================== SEED UOMs ====================
        print("\n📦 Seeding Units of Measure...")
        uoms_collection = db["uom_master"]
        await uoms_collection.delete_many({})
        
        uoms = [
            # Count
            {"uom_code": "PCS", "uom_name": "Pieces", "uom_group": "COUNT", "group_name": "Count", "uom_symbol": "pcs", "conversion_to_base": 1.0, "is_base_uom": True, "is_active": True, "display_order": 1, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "DOZ", "uom_name": "Dozen", "uom_group": "COUNT", "group_name": "Count", "uom_symbol": "doz", "conversion_to_base": 12.0, "is_base_uom": False, "is_active": True, "display_order": 2, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "GRS", "uom_name": "Gross", "uom_group": "COUNT", "group_name": "Count", "uom_symbol": "grs", "conversion_to_base": 144.0, "is_base_uom": False, "is_active": True, "display_order": 3, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "SET", "uom_name": "Set", "uom_group": "COUNT", "group_name": "Count", "uom_symbol": "set", "conversion_to_base": 1.0, "is_base_uom": False, "is_active": True, "display_order": 4, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "PAR", "uom_name": "Pair", "uom_group": "COUNT", "group_name": "Count", "uom_symbol": "pr", "conversion_to_base": 2.0, "is_base_uom": False, "is_active": True, "display_order": 5, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            # Length
            {"uom_code": "MTR", "uom_name": "Meter", "uom_group": "LENGTH", "group_name": "Length", "uom_symbol": "m", "conversion_to_base": 1.0, "is_base_uom": True, "is_active": True, "display_order": 1, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "CM", "uom_name": "Centimeter", "uom_group": "LENGTH", "group_name": "Length", "uom_symbol": "cm", "conversion_to_base": 0.01, "is_base_uom": False, "is_active": True, "display_order": 2, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "YRD", "uom_name": "Yard", "uom_group": "LENGTH", "group_name": "Length", "uom_symbol": "yd", "conversion_to_base": 0.9144, "is_base_uom": False, "is_active": True, "display_order": 3, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "IN", "uom_name": "Inch", "uom_group": "LENGTH", "group_name": "Length", "uom_symbol": "in", "conversion_to_base": 0.0254, "is_base_uom": False, "is_active": True, "display_order": 4, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            # Weight
            {"uom_code": "KG", "uom_name": "Kilogram", "uom_group": "WEIGHT", "group_name": "Weight", "uom_symbol": "kg", "conversion_to_base": 1.0, "is_base_uom": True, "is_active": True, "display_order": 1, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "GM", "uom_name": "Gram", "uom_group": "WEIGHT", "group_name": "Weight", "uom_symbol": "g", "conversion_to_base": 0.001, "is_base_uom": False, "is_active": True, "display_order": 2, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "LB", "uom_name": "Pound", "uom_group": "WEIGHT", "group_name": "Weight", "uom_symbol": "lb", "conversion_to_base": 0.453592, "is_base_uom": False, "is_active": True, "display_order": 3, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            # Area
            {"uom_code": "SQM", "uom_name": "Square Meter", "uom_group": "AREA", "group_name": "Area", "uom_symbol": "sq m", "conversion_to_base": 1.0, "is_base_uom": True, "is_active": True, "display_order": 1, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
            {"uom_code": "SQFT", "uom_name": "Square Feet", "uom_group": "AREA", "group_name": "Area", "uom_symbol": "sq ft", "conversion_to_base": 0.092903, "is_base_uom": False, "is_active": True, "display_order": 2, "created_date": datetime.utcnow(), "last_modified_date": datetime.utcnow()},
        ]
        
        result = await uoms_collection.insert_many(uoms)
        print(f"   ✅ Created {len(result.inserted_ids)} UOMs")
        
        # ==================== SUMMARY ====================
        print("\n" + "=" * 50)
        print("🎉 SEED DATA COMPLETE!")
        print("=" * 50)
        print("\n📋 Summary:")
        print("   • Users: 3 (admin@ccpl.com, manager@ccpl.com, user@ccpl.com)")
        print("   • Categories (Level 1): 4")
        print("   • Sub-Categories (Level 2): 7")
        print("   • Divisions (Level 3): 4")
        print("   • Classes (Level 4): 3")
        print("   • Sub-Classes (Level 5): 5")
        print("   • Brands: 5")
        print("   • Suppliers: 5")
        print("   • Colours: 15")
        print("   • Sizes: 14")
        print("   • UOMs: 14")
        print("\n🔐 Login Credentials:")
        print("   Admin:   admin@ccpl.com / Admin@123")
        print("   Manager: manager@ccpl.com / Manager@123")
        print("   User:    user@ccpl.com / User@123")
        print("\n✅ Database ready at MongoDB Atlas!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        client.close()
        print("\n👋 Connection closed.")


if __name__ == "__main__":
    asyncio.run(seed_database())
