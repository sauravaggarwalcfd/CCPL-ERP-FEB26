from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from ..models.customer import Customer
from ..core.dependencies import get_current_user

router = APIRouter()


class CustomerType(str, Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    DISTRIBUTOR = "distributor"


class AddressSchema(BaseModel):
    type: str  # billing, shipping
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    is_default: bool = False


class CustomerCreate(BaseModel):
    code: Optional[str] = None
    customer_type: str
    name: str
    email: Optional[EmailStr] = None
    phone: str
    alternate_phone: Optional[str] = None
    gst_number: Optional[str] = None
    addresses: List[AddressSchema] = []
    credit_limit: float = 0
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    customer_type: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None
    gst_number: Optional[str] = None
    addresses: Optional[List[AddressSchema]] = None
    credit_limit: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/")
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    customer_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_user),
):
    """List customers with filters"""
    query = {}
    if customer_type:
        query["customer_type"] = customer_type
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
            {"code": {"$regex": search, "$options": "i"}},
        ]
    
    customers = await Customer.find(query).skip(skip).limit(limit).to_list()
    total = await Customer.find(query).count()
    
    return {
        "data": customers,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/")
async def create_customer(
    data: CustomerCreate,
    current_user = Depends(get_current_user),
):
    """Create new customer"""
    customer = Customer(
        code=data.code,
        customer_type=data.customer_type,
        name=data.name,
        email=data.email,
        phone=data.phone,
        alternate_phone=data.alternate_phone,
        gst_number=data.gst_number,
        addresses=data.addresses,
        credit_limit=data.credit_limit,
        notes=data.notes,
    )
    
    await customer.insert()
    return customer


@router.get("/{customer_id}")
async def get_customer(
    customer_id: str,
    current_user = Depends(get_current_user),
):
    """Get customer details"""
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}")
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    current_user = Depends(get_current_user),
):
    """Update customer"""
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await customer.set(update_data)
    return customer


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user = Depends(get_current_user),
):
    """Soft delete customer"""
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.is_active = False
    customer.updated_at = datetime.utcnow()
    await customer.save()
    
    return {"message": "Customer deleted"}


@router.get("/{customer_id}/orders")
async def get_customer_orders(
    customer_id: str,
    current_user = Depends(get_current_user),
):
    """Get customer order history"""
    from app.models.sale_order import SaleOrder
    
    customer = await Customer.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    orders = await SaleOrder.find(SaleOrder.customer.id == customer_id).to_list()
    return {"orders": orders, "total": len(orders)}
