from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid
from ..models.product import Product, ProductVariant
from ..models.user import User
from ..core.dependencies import get_current_active_user, require_permissions

router = APIRouter()


class VariantCreate(BaseModel):
    color_name: str
    color_code: str
    color_hex: Optional[str] = None
    size_name: str
    size_type: str = "apparel"
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None


class ProductCreate(BaseModel):
    style_number: str
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    season_id: Optional[str] = None
    base_cost: float = 0
    base_price: float = 0
    hsn_code: Optional[str] = None
    gst_rate: float = 5.0
    material: Optional[str] = None
    care_instructions: Optional[str] = None
    variants: List[VariantCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_cost: Optional[float] = None
    base_price: Optional[float] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[float] = None
    is_active: Optional[bool] = None


@router.get("/")
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_permissions(["products.view"])),
):
    query = {}

    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"style_number": {"$regex": search, "$options": "i"}},
            {"variants.sku": {"$regex": search, "$options": "i"}},
        ]

    if category:
        query["category.slug"] = category

    if brand:
        query["brand.name"] = brand

    if is_active is not None:
        query["is_active"] = is_active

    skip = (page - 1) * limit

    products = await Product.find(query).skip(skip).limit(limit).to_list()
    total = await Product.find(query).count()

    return {
        "items": products,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(require_permissions(["products.create"])),
):
    # Check if style number exists
    existing = await Product.find_one(Product.style_number == data.style_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Style number already exists",
        )

    # Generate variants
    variants = []
    for v in data.variants:
        sku = f"{data.style_number}-{v.color_code}-{v.size_name}"
        variant = ProductVariant(
            id=uuid.uuid4().hex,
            sku=sku,
            color={"name": v.color_name, "code": v.color_code, "hex": v.color_hex},
            size={"name": v.size_name, "type": v.size_type},
            cost_price=v.cost_price or data.base_cost,
            selling_price=v.selling_price or data.base_price,
            mrp=v.mrp or data.base_price,
        )
        variants.append(variant)

    product = Product(
        style_number=data.style_number,
        name=data.name,
        description=data.description,
        base_cost=data.base_cost,
        base_price=data.base_price,
        hsn_code=data.hsn_code,
        gst_rate=data.gst_rate,
        material=data.material,
        care_instructions=data.care_instructions,
        variants=variants,
        created_by={"id": str(current_user.id), "name": current_user.full_name},
    )

    await product.insert()
    return product


@router.get("/{product_id}")
async def get_product(
    product_id: str,
    current_user: User = Depends(require_permissions(["products.view"])),
):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    data: ProductUpdate,
    current_user: User = Depends(require_permissions(["products.edit"])),
):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    await product.update({"$set": update_data})
    return await Product.get(product_id)


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    current_user: User = Depends(require_permissions(["products.delete"])),
):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Soft delete
    product.is_active = False
    product.updated_at = datetime.utcnow()
    await product.save()

    return {"message": "Product deleted successfully"}
