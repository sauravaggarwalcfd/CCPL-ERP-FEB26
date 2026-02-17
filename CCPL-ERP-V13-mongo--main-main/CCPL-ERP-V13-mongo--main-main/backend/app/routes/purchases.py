from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from ..models.purchase_order import PurchaseOrder
from ..core.dependencies import get_current_user

router = APIRouter()


class POStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    PARTIAL = "partial"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class POItemCreate(BaseModel):
    product_id: str
    variant_id: str
    ordered_qty: float
    unit_cost: float
    tax_rate: float = 0


class POCreate(BaseModel):
    supplier_id: str
    warehouse_id: str
    items: List[POItemCreate]
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None


class POUpdate(BaseModel):
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None


@router.get("/")
async def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    supplier_id: Optional[str] = None,
    current_user = Depends(get_current_user),
):
    """List purchase orders with filters"""
    query = {}
    if status:
        query["status"] = status
    if supplier_id:
        query["supplier.id"] = supplier_id
    
    pos = await PurchaseOrder.find(query).skip(skip).limit(limit).to_list()
    total = await PurchaseOrder.find(query).count()
    
    return {
        "data": pos,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/")
async def create_purchase_order(
    data: POCreate,
    current_user = Depends(get_current_user),
):
    """Create new purchase order"""
    from app.models.supplier import Supplier
    from app.models.warehouse import Warehouse
    
    supplier = await Supplier.get(data.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    warehouse = await Warehouse.get(data.warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Generate PO number
    po_number = await generate_po_number()
    
    # Calculate totals
    items = []
    subtotal = 0
    for item in data.items:
        item_total = item.ordered_qty * item.unit_cost
        tax_amount = item_total * (item.tax_rate / 100)
        items.append({
            "product_id": item.product_id,
            "variant_id": item.variant_id,
            "ordered_qty": item.ordered_qty,
            "received_qty": 0,
            "unit_cost": item.unit_cost,
            "tax_rate": item.tax_rate,
            "tax_amount": tax_amount,
            "total": item_total + tax_amount,
        })
        subtotal += item_total
    
    tax_amount = sum(i["tax_amount"] for i in items)
    total_amount = subtotal + tax_amount
    
    po = PurchaseOrder(
        po_number=po_number,
        supplier={"id": str(supplier.id), "code": supplier.code, "company_name": supplier.company_name},
        warehouse={"id": str(warehouse.id), "code": warehouse.code, "name": warehouse.name},
        status="draft",
        order_date=datetime.utcnow(),
        expected_date=data.expected_date,
        items=items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        notes=data.notes,
        terms_conditions=data.terms_conditions,
        created_by={"id": str(current_user.id), "name": current_user.full_name},
    )
    
    await po.insert()
    return po


@router.get("/{po_id}")
async def get_purchase_order(
    po_id: str,
    current_user = Depends(get_current_user),
):
    """Get purchase order details"""
    po = await PurchaseOrder.get(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.put("/{po_id}")
async def update_purchase_order(
    po_id: str,
    data: POUpdate,
    current_user = Depends(get_current_user),
):
    """Update purchase order (only draft status)"""
    po = await PurchaseOrder.get(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if po.status != "draft":
        raise HTTPException(status_code=400, detail="Can only update draft POs")
    
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await po.set(update_data)
    return po


@router.post("/{po_id}/confirm")
async def confirm_purchase_order(
    po_id: str,
    current_user = Depends(get_current_user),
):
    """Confirm purchase order"""
    po = await PurchaseOrder.get(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    po.status = "confirmed"
    po.updated_at = datetime.utcnow()
    await po.save()
    
    return po


@router.post("/{po_id}/receive")
async def receive_goods(
    po_id: str,
    items: List[dict],
    current_user = Depends(get_current_user),
):
    """Receive goods for purchase order"""
    from app.models.inventory import Inventory
    from app.models.stock_movement import StockMovement
    
    po = await PurchaseOrder.get(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    for receive_item in items:
        po_item = next((i for i in po.items if i.get("product_id") == receive_item["product_id"]), None)
        if not po_item:
            continue
        
        # Update received quantity
        po_item["received_qty"] += receive_item["received_qty"]
        
        # Update inventory
        inventory = await Inventory.find_one(
            (Inventory.product.id == po_item["product_id"]) &
            (Inventory.warehouse.id == po.warehouse["id"])
        )
        
        if inventory:
            inventory.quantity += receive_item["received_qty"]
            await inventory.save()
        else:
            inventory = Inventory(
                product={"id": po_item["product_id"]},
                variant={"id": po_item["variant_id"]},
                warehouse=po.warehouse,
                quantity=receive_item["received_qty"],
            )
            await inventory.insert()
        
        # Create stock movement
        await StockMovement(
            product={"id": po_item["product_id"]},
            variant={"id": po_item["variant_id"]},
            warehouse=po.warehouse,
            movement_type="PURCHASE_IN",
            quantity=receive_item["received_qty"],
            reference={"type": "purchase_order", "id": str(po.id), "number": po.po_number},
            created_by={"id": str(current_user.id), "name": current_user.full_name},
        ).insert()
    
    # Update PO status
    all_received = all(i.get("received_qty", 0) >= i.get("ordered_qty", 0) for i in po.items)
    any_received = any(i.get("received_qty", 0) > 0 for i in po.items)
    
    if all_received:
        po.status = "received"
        po.received_date = datetime.utcnow()
    elif any_received:
        po.status = "partial"
    
    po.updated_at = datetime.utcnow()
    await po.save()
    
    return po


async def generate_po_number() -> str:
    """Generate next PO number"""
    from app.models.settings import Settings
    
    settings = await Settings.find_one()
    if not settings:
        settings = Settings(sequences={"purchase_order": 0})
        await settings.insert()
    
    settings.sequences["purchase_order"] += 1
    await settings.save()
    
    year = datetime.utcnow().year
    seq = str(settings.sequences["purchase_order"]).zfill(4)
    return f"PO-{year}-{seq}"
