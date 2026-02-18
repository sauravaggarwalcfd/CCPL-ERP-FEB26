from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import logging
from .database import connect_to_sheets, close_sheets_connection
from .routes import (
    auth,
    users,
    roles,
    products,
    inventory,
    suppliers,
    purchases,
    purchase_orders,
    customers,
    sales,
    warehouses,
    transfers,
    adjustments,
    master_data,
    reports,
    items,
    item_types,
    category_hierarchy,
    colours,
    sizes,
    uoms,
    variant_groups,
    specifications,
    brands,
    files,
    bom,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await connect_to_sheets()
        logger.info("Google Sheets database connection successful")
    except Exception as e:
        logger.warning(f"Sheets database connection failed: {str(e)}")
        logger.warning("App starting with database unavailable - use for testing only")
    yield
    # Shutdown
    try:
        await close_sheets_connection()
    except Exception as e:
        logger.warning(f"Error closing database connection: {str(e)}")


app = FastAPI(
    title="Inventory Management ERP",
    description="API for Confidence Clothing Inventory System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - Allow localhost and all Codespaces URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8085",
        "http://127.0.0.1:8085",
    ],
    allow_origin_regex=r"https://.*\.app\.github\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["Suppliers"])
app.include_router(purchases.router, prefix="/api/purchase-orders-old", tags=["Purchases-Old"])
app.include_router(purchase_orders.router, prefix="/api/po", tags=["Purchase Orders"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(sales.router, prefix="/api/sale-orders", tags=["Sales"])
app.include_router(warehouses.router, prefix="/api/warehouses", tags=["Warehouses"])
app.include_router(transfers.router, prefix="/api/transfers", tags=["Transfers"])
app.include_router(
    adjustments.router, prefix="/api/adjustments", tags=["Adjustments"]
)
app.include_router(
    master_data.router, prefix="/api/master-data", tags=["Master Data"]
)
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(item_types.router, prefix="/api/item-types", tags=["Item Types"])
app.include_router(category_hierarchy.router, prefix="/api/hierarchy", tags=["Category Hierarchy"])
app.include_router(brands.router, prefix="/api/brands", tags=["Brand Master"])
app.include_router(files.router, prefix="/api/files", tags=["File Management"])

# Variant Master routes
app.include_router(colours.router, prefix="/api", tags=["Colour Master"])
app.include_router(sizes.router, prefix="/api", tags=["Size Master"])
app.include_router(uoms.router, prefix="/api", tags=["UOM Master"])
app.include_router(variant_groups.router, prefix="/api", tags=["Variant Groups"])

# Specifications routes
app.include_router(specifications.router, prefix="/api", tags=["Specifications"])

# Dyeing BOM Module (Google Sheets-backed)
app.include_router(bom.router, prefix="/api/bom", tags=["Dyeing BOM"])

# Serve uploaded files statically
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
async def root():
    return {"message": "Inventory ERP API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


