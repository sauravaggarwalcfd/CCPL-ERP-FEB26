from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.transfer import StockTransfer
from ..core.dependencies import get_current_user

router = APIRouter()


class TransferItemCreate(BaseModel):
    product_id: str
    variant_id: str
    requested_qty: float


class TransferCreate(BaseModel):
    from_warehouse_id: str
    to_warehouse_id: str
    items: List[TransferItemCreate]
    notes: Optional[str] = None


class ReceiveTransferItem(BaseModel):
    item_id: str
    received_qty: float


@router.get("/")
async def list_transfers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    current_user = Depends(get_current_user),
):
    """List transfers"""
    query = {}
    if status:
        query["status"] = status
    
    transfers = await StockTransfer.find(query).skip(skip).limit(limit).to_list()
    total = await StockTransfer.find(query).count()
    
    return {
        "data": transfers,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/")
async def create_transfer(
    data: TransferCreate,
    current_user = Depends(get_current_user),
):
    """Create stock transfer"""
    from ..models.warehouse import Warehouse
    
    if data.from_warehouse_id == data.to_warehouse_id:
        raise HTTPException(status_code=400, detail="Source and destination warehouses must be different")
    
    from_wh = await Warehouse.get(data.from_warehouse_id)
    to_wh = await Warehouse.get(data.to_warehouse_id)
    
    if not from_wh or not to_wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Generate transfer number
    transfer_number = await generate_transfer_number()
    
    items = []
    for item in data.items:
        items.append({
            "product_id": item.product_id,
            "variant_id": item.variant_id,
            "requested_qty": item.requested_qty,
            "shipped_qty": 0,
            "received_qty": 0,
        })
    
    transfer = StockTransfer(
        transfer_number=transfer_number,
        from_warehouse={"id": str(from_wh.id), "code": from_wh.code, "name": from_wh.name},
        to_warehouse={"id": str(to_wh.id), "code": to_wh.code, "name": to_wh.name},
        status="draft",
        items=items,
        notes=data.notes,
        created_by={"id": str(current_user.id), "name": current_user.full_name},
    )
    
    await transfer.insert()
    return transfer


@router.get("/{transfer_id}")
async def get_transfer(
    transfer_id: str,
    current_user = Depends(get_current_user),
):
    """Get transfer details"""
    transfer = await StockTransfer.get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@router.post("/{transfer_id}/approve")
async def approve_transfer(
    transfer_id: str,
    current_user = Depends(get_current_user),
):
    """Approve transfer"""
    transfer = await StockTransfer.get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    if transfer.status != "draft":
        raise HTTPException(status_code=400, detail="Can only approve draft transfers")
    
    transfer.status = "approved"
    transfer.approved_by = {"id": str(current_user.id), "name": current_user.full_name}
    transfer.approved_at = datetime.utcnow()
    transfer.updated_at = datetime.utcnow()
    await transfer.save()
    
    return transfer


@router.post("/{transfer_id}/ship")
async def ship_transfer(
    transfer_id: str,
    current_user = Depends(get_current_user),
):
    """Ship transfer and deduct from source"""
    from ..models.inventory import Inventory
    from ..models.stock_movement import StockMovement
    
    transfer = await StockTransfer.get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    if transfer.status != "approved":
        raise HTTPException(status_code=400, detail="Can only ship approved transfers")
    
    # Check and deduct stock
    for item in transfer.items:
        inventory = await Inventory.find_one(
            (Inventory.variant.id == item["variant_id"]) &
            (Inventory.warehouse.id == transfer.from_warehouse["id"])
        )
        
        available = (inventory.quantity - inventory.reserved_quantity) if inventory else 0
        
        if available < item["requested_qty"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item['variant_id']}"
            )
        
        # Deduct from source
        inventory.quantity -= item["requested_qty"]
        await inventory.save()
        
        # Create movement
        await StockMovement(
            product={"id": item["product_id"]},
            variant={"id": item["variant_id"]},
            warehouse=transfer.from_warehouse,
            movement_type="TRANSFER_OUT",
            quantity=-item["requested_qty"],
            reference={"type": "transfer", "id": str(transfer.id), "number": transfer.transfer_number},
            created_by={"id": str(current_user.id), "name": current_user.full_name},
        ).insert()
        
        item["shipped_qty"] = item["requested_qty"]
    
    transfer.status = "in_transit"
    transfer.shipped_at = datetime.utcnow()
    transfer.updated_at = datetime.utcnow()
    await transfer.save()
    
    return transfer


@router.post("/{transfer_id}/receive")
async def receive_transfer(
    transfer_id: str,
    items: List[ReceiveTransferItem],
    current_user = Depends(get_current_user),
):
    """Receive transfer at destination"""
    from ..models.inventory import Inventory
    from ..models.stock_movement import StockMovement
    
    transfer = await StockTransfer.get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    if transfer.status != "in_transit":
        raise HTTPException(status_code=400, detail="Can only receive in-transit transfers")
    
    for receive_item in items:
        item = next((i for i in transfer.items if i.get("product_id") == receive_item.item_id), None)
        if not item:
            continue
        
        item["received_qty"] = receive_item.received_qty
        
        # Add to destination
        dest_inventory = await Inventory.find_one(
            (Inventory.variant.id == item["variant_id"]) &
            (Inventory.warehouse.id == transfer.to_warehouse["id"])
        )
        
        if dest_inventory:
            dest_inventory.quantity += receive_item.received_qty
            await dest_inventory.save()
        else:
            dest_inventory = Inventory(
                product={"id": item["product_id"]},
                variant={"id": item["variant_id"]},
                warehouse=transfer.to_warehouse,
                quantity=receive_item.received_qty,
            )
            await dest_inventory.insert()
        
        # Create movement
        await StockMovement(
            product={"id": item["product_id"]},
            variant={"id": item["variant_id"]},
            warehouse=transfer.to_warehouse,
            movement_type="TRANSFER_IN",
            quantity=receive_item.received_qty,
            reference={"type": "transfer", "id": str(transfer.id), "number": transfer.transfer_number},
            created_by={"id": str(current_user.id), "name": current_user.full_name},
        ).insert()
    
    transfer.status = "completed"
    transfer.received_at = datetime.utcnow()
    transfer.updated_at = datetime.utcnow()
    await transfer.save()
    
    return transfer


@router.delete("/{transfer_id}")
async def cancel_transfer(
    transfer_id: str,
    current_user = Depends(get_current_user),
):
    """Cancel transfer"""
    transfer = await StockTransfer.get(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    transfer.status = "cancelled"
    transfer.updated_at = datetime.utcnow()
    await transfer.save()
    
    return {"message": "Transfer cancelled"}


async def generate_transfer_number() -> str:
    """Generate next transfer number"""
    from ..models.settings import Settings
    
    settings = await Settings.find_one()
    if not settings:
        settings = Settings(sequences={"transfer": 0})
        await settings.insert()
    
    settings.sequences["transfer"] += 1
    await settings.save()
    
    year = datetime.utcnow().year
    seq = str(settings.sequences["transfer"]).zfill(4)
    return f"TRF-{year}-{seq}"
