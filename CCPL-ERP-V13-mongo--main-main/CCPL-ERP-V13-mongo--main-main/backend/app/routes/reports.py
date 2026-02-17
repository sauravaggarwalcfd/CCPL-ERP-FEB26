from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, date
from ..core.dependencies import get_current_user
from ..models.inventory import Inventory
from ..models.sale_order import SaleOrder
from ..models.purchase_order import PurchaseOrder
from ..models.stock_movement import StockMovement

router = APIRouter()


@router.get("/stock/current")
async def current_stock_report(
    warehouse_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user = Depends(get_current_user),
):
    """Current stock levels report"""
    query = {}
    if warehouse_id:
        query["warehouse.id"] = warehouse_id
    
    inventory = await Inventory.find(query).skip(skip).limit(limit).to_list()
    total = await Inventory.find(query).count()
    
    # Calculate totals
    total_value = sum(item.quantity * item.cost_price for item in inventory if hasattr(item, 'cost_price'))
    
    return {
        "items": inventory,
        "summary": {
            "total_items": len(inventory),
            "total_quantity": sum(item.quantity for item in inventory),
            "total_value": total_value,
        },
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
        },
    }


@router.get("/stock/low")
async def low_stock_report(
    warehouse_id: Optional[str] = None,
    current_user = Depends(get_current_user),
):
    """Low stock items report"""
    query = {"$expr": {"$lte": ["$quantity", "$min_stock_level"]}}
    if warehouse_id:
        query["warehouse.id"] = warehouse_id
    
    items = await Inventory.find(query).to_list()
    
    return {
        "items": items,
        "total": len(items),
    }


@router.get("/stock/movements")
async def stock_movements_report(
    start_date: date,
    end_date: date,
    warehouse_id: Optional[str] = None,
    movement_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user = Depends(get_current_user),
):
    """Stock movement history"""
    from datetime import datetime as dt
    
    query = {
        "created_at": {
            "$gte": dt.combine(start_date, dt.min.time()),
            "$lte": dt.combine(end_date, dt.max.time()),
        }
    }
    
    if warehouse_id:
        query["warehouse.id"] = warehouse_id
    if movement_type:
        query["movement_type"] = movement_type
    
    movements = await StockMovement.find(query).skip(skip).limit(limit).to_list()
    total = await StockMovement.find(query).count()
    
    return {
        "items": movements,
        "total": total,
        "pagination": {"skip": skip, "limit": limit},
    }


@router.get("/sales/summary")
async def sales_summary(
    start_date: date,
    end_date: date,
    current_user = Depends(get_current_user),
):
    """Sales summary report"""
    from datetime import datetime as dt
    
    query = {
        "order_date": {
            "$gte": dt.combine(start_date, dt.min.time()),
            "$lte": dt.combine(end_date, dt.max.time()),
        },
        "status": {"$nin": ["cancelled", "returned"]},
    }
    
    orders = await SaleOrder.find(query).to_list()
    
    total_orders = len(orders)
    total_revenue = sum(order.total_amount for order in orders)
    total_items = sum(sum(item.get("quantity", 0) for item in order.items) for order in orders)
    
    return {
        "period": {"start": start_date, "end": end_date},
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_items_sold": total_items,
            "avg_order_value": total_revenue / total_orders if total_orders > 0 else 0,
        },
        "orders": orders,
    }


@router.get("/sales/by-product")
async def sales_by_product(
    start_date: date,
    end_date: date,
    current_user = Depends(get_current_user),
):
    """Sales by product report"""
    from datetime import datetime as dt
    from collections import defaultdict
    
    query = {
        "order_date": {
            "$gte": dt.combine(start_date, dt.min.time()),
            "$lte": dt.combine(end_date, dt.max.time()),
        },
        "status": {"$nin": ["cancelled", "returned"]},
    }
    
    orders = await SaleOrder.find(query).to_list()
    
    product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    
    for order in orders:
        for item in order.items:
            product_id = item.get("product_id")
            qty = item.get("quantity", 0)
            total = item.get("total", 0)
            
            product_sales[product_id]["quantity"] += qty
            product_sales[product_id]["revenue"] += total
    
    return {
        "period": {"start": start_date, "end": end_date},
        "products": [
            {
                "product_id": pid,
                "quantity": data["quantity"],
                "revenue": data["revenue"],
            }
            for pid, data in sorted(
                product_sales.items(),
                key=lambda x: x[1]["revenue"],
                reverse=True,
            )
        ],
    }


@router.get("/purchases/summary")
async def purchases_summary(
    start_date: date,
    end_date: date,
    current_user = Depends(get_current_user),
):
    """Purchase summary report"""
    from datetime import datetime as dt
    
    query = {
        "order_date": {
            "$gte": dt.combine(start_date, dt.min.time()),
            "$lte": dt.combine(end_date, dt.max.time()),
        },
    }
    
    orders = await PurchaseOrder.find(query).to_list()
    
    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders)
    
    return {
        "period": {"start": start_date, "end": end_date},
        "summary": {
            "total_orders": total_orders,
            "total_amount": total_amount,
            "avg_order_value": total_amount / total_orders if total_orders > 0 else 0,
        },
        "orders": orders,
    }
