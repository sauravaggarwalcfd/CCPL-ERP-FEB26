from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from ..models.sale_order import SaleOrder
from ..core.dependencies import get_current_user

router = APIRouter()


class SOItemCreate(BaseModel):
    product_id: str
    variant_id: str
    quantity: float
    unit_price: float
    tax_rate: float = 0
    discount: float = 0


class AddressSchema(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    pincode: str


class SOCreate(BaseModel):
    customer_id: str
    warehouse_id: str
    items: List[SOItemCreate]
    shipping_address: AddressSchema
    billing_address: AddressSchema
    payment_method: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
async def list_sale_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    current_user = Depends(get_current_user),
):
    """List sale orders with filters"""
    query = {}
    if status:
        query["status"] = status
    if payment_status:
        query["payment_status"] = payment_status
    
    orders = await SaleOrder.find(query).skip(skip).limit(limit).to_list()
    total = await SaleOrder.find(query).count()
    
    return {
        "data": orders,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/")
async def create_sale_order(
    data: SOCreate,
    current_user = Depends(get_current_user),
):
    """Create new sale order"""
    from ..models.customer import Customer
    from ..models.warehouse import Warehouse
    from ..models.inventory import Inventory
    
    customer = await Customer.get(data.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    warehouse = await Warehouse.get(data.warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Generate SO number
    so_number = await generate_so_number()
    
    # Calculate totals and check stock
    items = []
    subtotal = 0
    for item in data.items:
        # Check stock availability
        inventory = await Inventory.find_one(
            (Inventory.variant.id == item.variant_id) &
            (Inventory.warehouse.id == data.warehouse_id)
        )
        
        available = (inventory.quantity - inventory.reserved_quantity) if inventory else 0
        if available < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for variant {item.variant_id}"
            )
        
        item_total = item.quantity * item.unit_price
        discount_amount = item_total * (item.discount / 100) if item.discount else 0
        tax_amount = (item_total - discount_amount) * (item.tax_rate / 100) if item.tax_rate else 0
        
        items.append({
            "product_id": item.product_id,
            "variant_id": item.variant_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "tax_rate": item.tax_rate,
            "tax_amount": tax_amount,
            "discount": item.discount,
            "discount_amount": discount_amount,
            "total": item_total - discount_amount + tax_amount,
        })
        subtotal += item_total
    
    discount_amount = sum(i["discount_amount"] for i in items)
    tax_amount = sum(i["tax_amount"] for i in items)
    total_amount = subtotal - discount_amount + tax_amount
    
    so = SaleOrder(
        order_number=so_number,
        customer={"id": str(customer.id), "name": customer.name, "phone": customer.phone},
        warehouse={"id": str(warehouse.id), "code": warehouse.code, "name": warehouse.name},
        status="pending",
        order_date=datetime.utcnow(),
        shipping_address=data.shipping_address.dict(),
        billing_address=data.billing_address.dict(),
        items=items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        payment_status="pending",
        payment_method=data.payment_method,
        notes=data.notes,
        created_by={"id": str(current_user.id), "name": current_user.full_name},
    )
    
    await so.insert()
    return so


@router.get("/{so_id}")
async def get_sale_order(
    so_id: str,
    current_user = Depends(get_current_user),
):
    """Get sale order details"""
    so = await SaleOrder.get(so_id)
    if not so:
        raise HTTPException(status_code=404, detail="Sale order not found")
    return so


@router.post("/{so_id}/confirm")
async def confirm_order(
    so_id: str,
    current_user = Depends(get_current_user),
):
    """Confirm order and reserve stock"""
    from ..models.inventory import Inventory
    
    so = await SaleOrder.get(so_id)
    if not so:
        raise HTTPException(status_code=404, detail="Sale order not found")
    
    # Reserve stock
    for item in so.items:
        inventory = await Inventory.find_one(
            (Inventory.variant.id == item["variant_id"]) &
            (Inventory.warehouse.id == so.warehouse["id"])
        )
        
        if inventory:
            inventory.reserved_quantity += item["quantity"]
            await inventory.save()
    
    so.status = "confirmed"
    so.updated_at = datetime.utcnow()
    await so.save()
    
    return so


@router.post("/{so_id}/fulfill")
async def fulfill_order(
    so_id: str,
    current_user = Depends(get_current_user),
):
    """Fulfill order and deduct stock"""
    from ..models.inventory import Inventory
    from ..models.stock_movement import StockMovement
    
    so = await SaleOrder.get(so_id)
    if not so:
        raise HTTPException(status_code=404, detail="Sale order not found")
    
    for item in so.items:
        inventory = await Inventory.find_one(
            (Inventory.variant.id == item["variant_id"]) &
            (Inventory.warehouse.id == so.warehouse["id"])
        )
        
        if inventory:
            inventory.quantity -= item["quantity"]
            inventory.reserved_quantity -= item["quantity"]
            await inventory.save()
        
        # Create stock movement
        await StockMovement(
            product={"id": item["product_id"]},
            variant={"id": item["variant_id"]},
            warehouse=so.warehouse,
            movement_type="SALE_OUT",
            quantity=-item["quantity"],
            reference={"type": "sale_order", "id": str(so.id), "number": so.order_number},
            created_by={"id": str(current_user.id), "name": current_user.full_name},
        ).insert()
    
    so.status = "shipped"
    so.shipped_at = datetime.utcnow()
    so.updated_at = datetime.utcnow()
    await so.save()
    
    return so


@router.delete("/{so_id}")
async def cancel_order(
    so_id: str,
    current_user = Depends(get_current_user),
):
    """Cancel order and release reserved stock"""
    from ..models.inventory import Inventory
    
    so = await SaleOrder.get(so_id)
    if not so:
        raise HTTPException(status_code=404, detail="Sale order not found")
    
    if so.status == "confirmed":
        # Release reserved stock
        for item in so.items:
            inventory = await Inventory.find_one(
                (Inventory.variant.id == item["variant_id"]) &
                (Inventory.warehouse.id == so.warehouse["id"])
            )
            
            if inventory:
                inventory.reserved_quantity -= item["quantity"]
                await inventory.save()
    
    so.status = "cancelled"
    so.updated_at = datetime.utcnow()
    await so.save()
    
    return {"message": "Order cancelled"}


async def generate_so_number() -> str:
    """Generate next SO number"""
    from ..models.settings import Settings
    
    settings = await Settings.find_one()
    if not settings:
        settings = Settings(sequences={"sale_order": 0})
        await settings.insert()
    
    settings.sequences["sale_order"] += 1
    await settings.save()
    
    year = datetime.utcnow().year
    seq = str(settings.sequences["sale_order"]).zfill(4)
    return f"SO-{year}-{seq}"
