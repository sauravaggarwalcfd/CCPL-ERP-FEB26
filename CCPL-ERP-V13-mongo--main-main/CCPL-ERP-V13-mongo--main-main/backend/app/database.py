"""Database layer — MongoDB Atlas via Motor + Beanie."""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings

logger = logging.getLogger(__name__)
_client = None


async def connect_to_mongo():
    global _client
    try:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = _client[settings.DATABASE_NAME]

        from .models.user import User
        from .models.role import Role, Permission
        from .models.product import Product
        from .models.inventory import Inventory
        from .models.supplier import Supplier
        from .models.supplier_master import SupplierMaster
        from .models.purchase_order import PurchaseOrder
        from .models.customer import Customer
        from .models.sale_order import SaleOrder
        from .models.warehouse import Warehouse
        from .models.stock_movement import StockMovement
        from .models.transfer import StockTransfer
        from .models.adjustment import StockAdjustment
        from .models.audit_log import AuditLog
        from .models.settings import AppSettings
        from .models.item import ItemMaster
        from .models.item_type import ItemType
        from .models.category_hierarchy import (
            ItemCategory, ItemSubCategory, ItemDivision, ItemClass, ItemSubClass
        )
        from .models.colour_master import ColourMaster
        from .models.size_master import SizeMaster
        from .models.uom_master import UOMMaster
        from .models.variant_groups import VariantGroup
        from .models.brand_master import BrandMaster
        from .models.specifications import CategorySpecifications, ItemSpecifications
        from .models.file_master import FileMaster
        from .models.master_data import Category, Brand, Season, Color, Size

        await init_beanie(
            database=db,
            document_models=[
                User, Role, Permission,
                Product, Inventory,
                Supplier, SupplierMaster,
                PurchaseOrder, Customer, SaleOrder,
                Warehouse, StockMovement, StockTransfer, StockAdjustment,
                AuditLog, AppSettings,
                ItemMaster, ItemType,
                ItemCategory, ItemSubCategory, ItemDivision, ItemClass, ItemSubClass,
                ColourMaster, SizeMaster, UOMMaster, VariantGroup, BrandMaster,
                CategorySpecifications, ItemSpecifications,
                FileMaster, Category, Brand, Season, Color, Size,
            ],
        )
        logger.info(f"MongoDB Atlas connected: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise


async def close_mongo_connection():
    global _client
    if _client:
        _client.close()

# Aliases used by main.py
connect_to_sheets = connect_to_mongo
close_sheets_connection = close_mongo_connection
