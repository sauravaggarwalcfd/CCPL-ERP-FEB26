"""
Purchase Order API Routes
Complete PO management with calculations, workflow, and integrations
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from datetime import datetime, date, timedelta
import uuid
import logging

from ..models.purchase_order import (
    PurchaseOrder, POStatus, POCreate, POUpdate, POStatusUpdate,
    POApprovalUpdate, POLineItemCreate, POSupplierInfo, POLineItem,
    POSummary, PODelivery, POPayment, POApproval, POTracking
)
from ..core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== HELPER FUNCTIONS ====================

async def generate_po_number() -> str:
    """Generate unique PO number in format: PO-YYYY-MM-XXXX"""
    from datetime import datetime

    # Get current year and month
    now = datetime.utcnow()
    year = now.year
    month = str(now.month).zfill(2)

    # Find last PO number for current month
    prefix = f"PO-{year}-{month}"
    last_po = await PurchaseOrder.find(
        PurchaseOrder.po_number.startswith(prefix)
    ).sort("-po_number").limit(1).to_list()

    if last_po:
        # Extract sequence number and increment
        last_seq = int(last_po[0].po_number.split("-")[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    # Format: PO-YYYY-MM-XXXX
    po_number = f"{prefix}-{str(new_seq).zfill(4)}"

    # Verify uniqueness
    existing = await PurchaseOrder.find_one(PurchaseOrder.po_number == po_number)
    if existing:
        # If exists (shouldn't happen), add timestamp
        po_number = f"{prefix}-{str(new_seq).zfill(4)}-{now.strftime('%H%M%S')}"

    return po_number


async def get_supplier_info(supplier_code: str) -> POSupplierInfo:
    """Get supplier information from Supplier Master"""
    # TODO: Replace with actual Supplier model import
    # For now, return basic info - integrate with your Supplier Master
    try:
        # from ..models.supplier import Supplier
        # supplier = await Supplier.find_one(Supplier.code == supplier_code)
        # if not supplier:
        #     raise HTTPException(404, f"Supplier {supplier_code} not found")

        # For now, return placeholder
        return POSupplierInfo(
            code=supplier_code,
            name=f"Supplier {supplier_code}",
            gstin="",
            payment_method="BANK_TRANSFER",
            payment_terms="NET 30"
        )
    except Exception as e:
        logger.error(f"Error fetching supplier: {e}")
        raise HTTPException(404, f"Supplier {supplier_code} not found")


async def get_item_info(item_code: str) -> dict:
    """Get item information from Item Master"""
    # TODO: Replace with actual Item model import
    # For now, return basic info - integrate with your Item Master
    try:
        # from ..models.item import Item
        # item = await Item.find_one(Item.code == item_code)
        # if not item:
        #     raise HTTPException(404, f"Item {item_code} not found")

        # Return item details including HSN, GST, etc.
        return {
            "item_code": item_code,
            "item_name": f"Item {item_code}",
            "item_description": "",
            "item_category": "",
            "hsn_code": "",
            "gst_percent": 18.0,  # Default GST
            "unit": "PCS"
        }
    except Exception as e:
        logger.error(f"Error fetching item: {e}")
        raise HTTPException(404, f"Item {item_code} not found")


def calculate_line_item(item: POLineItemCreate, line_number: int, supplier_state: str = "DELHI") -> POLineItem:
    """Calculate all amounts for a line item"""

    # Basic calculations
    line_amount = round(item.quantity * item.unit_rate, 2)
    discount_amount = round(line_amount * (item.discount_percent / 100), 2)
    taxable_amount = round(line_amount - discount_amount, 2)

    # GST calculations (split based on state)
    gst_percent = item.gst_percent

    # Check if inter-state or intra-state (simplified - you should use actual state comparison)
    is_interstate = False  # TODO: Compare supplier state with company state

    if is_interstate:
        # IGST
        igst_percent = gst_percent
        cgst_percent = 0
        sgst_percent = 0
        igst_amount = round(taxable_amount * (igst_percent / 100), 2)
        cgst_amount = 0
        sgst_amount = 0
    else:
        # CGST + SGST
        cgst_percent = gst_percent / 2
        sgst_percent = gst_percent / 2
        igst_percent = 0
        cgst_amount = round(taxable_amount * (cgst_percent / 100), 2)
        sgst_amount = round(taxable_amount * (sgst_percent / 100), 2)
        igst_amount = 0

    gst_amount = cgst_amount + sgst_amount + igst_amount
    net_amount = round(taxable_amount + gst_amount, 2)

    return POLineItem(
        line_number=line_number,
        item_code=item.item_code,
        item_name=item.item_name,
        item_description=item.item_description,
        item_category=item.item_category,
        quantity=item.quantity,
        unit=item.unit,
        unit_rate=item.unit_rate,
        line_amount=line_amount,
        discount_percent=item.discount_percent,
        discount_amount=discount_amount,
        taxable_amount=taxable_amount,
        hsn_code=item.hsn_code,
        gst_percent=gst_percent,
        cgst_percent=cgst_percent,
        sgst_percent=sgst_percent,
        igst_percent=igst_percent,
        gst_amount=gst_amount,
        cgst_amount=cgst_amount,
        sgst_amount=sgst_amount,
        igst_amount=igst_amount,
        net_amount=net_amount,
        expected_delivery_date=item.expected_delivery_date,
        inspection_required=item.inspection_required,
        quality_specs=item.quality_specs,
        notes=item.notes,
        received_quantity=0,
        pending_quantity=item.quantity
    )


def calculate_summary(items: List[POLineItem]) -> POSummary:
    """Calculate PO summary totals"""

    subtotal = sum(item.line_amount for item in items)
    total_discount = sum(item.discount_amount for item in items)
    total_taxable = sum(item.taxable_amount for item in items)
    total_cgst = sum(item.cgst_amount for item in items)
    total_sgst = sum(item.sgst_amount for item in items)
    total_igst = sum(item.igst_amount for item in items)
    total_gst = total_cgst + total_sgst + total_igst

    # Calculate grand total before rounding
    grand_total_raw = total_taxable + total_gst

    # Round off to nearest integer
    grand_total = round(grand_total_raw)
    round_off = round(grand_total - grand_total_raw, 2)

    return POSummary(
        subtotal=round(subtotal, 2),
        total_discount=round(total_discount, 2),
        total_taxable=round(total_taxable, 2),
        total_cgst=round(total_cgst, 2),
        total_sgst=round(total_sgst, 2),
        total_igst=round(total_igst, 2),
        total_gst=round(total_gst, 2),
        round_off=round_off,
        grand_total=grand_total
    )


# ==================== API ENDPOINTS ====================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    data: POCreate,
    current_user = Depends(get_current_user)
):
    """Create new Purchase Order"""

    try:
        # Get supplier information
        supplier_info = await get_supplier_info(data.supplier_code)

        # Process line items with calculations
        line_items = []
        for idx, item_data in enumerate(data.items, 1):
            # Get item details from Item Master (if needed)
            # item_info = await get_item_info(item_data.item_code)

            # Calculate line item
            line_item = calculate_line_item(item_data, idx)
            line_items.append(line_item)

        # Calculate summary
        summary = calculate_summary(line_items)

        # Create delivery info
        delivery = PODelivery(
            location=data.delivery_location,
            method=data.delivery_method,
            lead_time_days=data.lead_time_days,
            expected_delivery_date=data.po_date + timedelta(days=data.lead_time_days)
        )

        # Create payment info
        payment = POPayment(
            terms=data.payment_terms,
            method=data.payment_method,
            currency=data.currency
        )

        # Create tracking info
        tracking = POTracking(
            created_by=current_user.get("email", "unknown")
        )

        # Create approval info
        approval = POApproval(
            approval_status="PENDING"
        )

        # Generate PO number
        po_number = await generate_po_number()

        # Create PO
        po = PurchaseOrder(
            po_number=po_number,
            po_version=1,
            po_date=data.po_date,
            po_status=POStatus.DRAFT,
            indent_number=data.indent_number,
            supplier=supplier_info,
            items=line_items,
            summary=summary,
            delivery=delivery,
            payment=payment,
            approval=approval,
            tracking=tracking,
            cost_center=data.cost_center,
            project_code=data.project_code,
            department=data.department,
            sample_attached=data.sample_attached,
            remarks=data.remarks,
            terms_and_conditions=data.terms_and_conditions,
            is_active=True,
            is_deleted=False
        )

        # Save to database
        await po.insert()

        logger.info(f"Created PO: {po.po_number}")

        return {
            "message": "Purchase Order created successfully",
            "po_number": po.po_number,
            "po_id": str(po.id),
            "grand_total": po.summary.grand_total
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating PO: {e}")
        raise HTTPException(500, f"Failed to create PO: {str(e)}")


@router.get("/")
async def list_purchase_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    supplier_code: Optional[str] = None,
    po_number: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    current_user = Depends(get_current_user)
):
    """List all Purchase Orders with filters"""

    try:
        # Build query
        query = {"is_deleted": False}

        if status:
            query["po_status"] = status

        if supplier_code:
            query["supplier.code"] = supplier_code

        if po_number:
            query["po_number"] = {"$regex": po_number, "$options": "i"}

        if from_date:
            query["po_date"] = {"$gte": from_date}

        if to_date:
            if "po_date" in query:
                query["po_date"]["$lte"] = to_date
            else:
                query["po_date"] = {"$lte": to_date}

        # Get total count
        total = await PurchaseOrder.find(query).count()

        # Get POs
        pos = await PurchaseOrder.find(query).skip(skip).limit(limit).sort("-po_date").to_list()

        # Format response
        result = []
        for po in pos:
            result.append({
                "id": str(po.id),
                "po_number": po.po_number,
                "po_date": po.po_date,
                "po_status": po.po_status,
                "supplier_code": po.supplier.code,
                "supplier_name": po.supplier.name,
                "total_items": len(po.items),
                "grand_total": po.summary.grand_total,
                "created_by": po.tracking.created_by,
                "created_date": po.tracking.created_date
            })

        return {
            "data": result,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error listing POs: {e}")
        raise HTTPException(500, f"Failed to list POs: {str(e)}")


@router.get("/{po_number}")
async def get_purchase_order(
    po_number: str,
    current_user = Depends(get_current_user)
):
    """Get single Purchase Order by PO number"""

    try:
        po = await PurchaseOrder.find_one(PurchaseOrder.po_number == po_number)

        if not po:
            raise HTTPException(404, f"Purchase Order {po_number} not found")

        return {
            "id": str(po.id),
            "po_number": po.po_number,
            "po_version": po.po_version,
            "po_date": po.po_date,
            "po_status": po.po_status,
            "indent_number": po.indent_number,
            "supplier": po.supplier.dict(),
            "items": [item.dict() for item in po.items],
            "summary": po.summary.dict(),
            "delivery": po.delivery.dict(),
            "payment": po.payment.dict(),
            "approval": po.approval.dict(),
            "tracking": po.tracking.dict(),
            "cost_center": po.cost_center,
            "project_code": po.project_code,
            "department": po.department,
            "sample_attached": po.sample_attached,
            "remarks": po.remarks,
            "terms_and_conditions": po.terms_and_conditions,
            "attachments": po.attachments
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting PO: {e}")
        raise HTTPException(500, f"Failed to get PO: {str(e)}")


@router.put("/{po_number}")
async def update_purchase_order(
    po_number: str,
    data: POUpdate,
    current_user = Depends(get_current_user)
):
    """Update Purchase Order (only DRAFT status)"""

    try:
        po = await PurchaseOrder.find_one(PurchaseOrder.po_number == po_number)

        if not po:
            raise HTTPException(404, f"Purchase Order {po_number} not found")

        # Only allow updates for DRAFT status
        if po.po_status not in [POStatus.DRAFT]:
            raise HTTPException(400, "Can only update PO in DRAFT status")

        # Update fields
        update_data = data.dict(exclude_unset=True)

        if "items" in update_data:
            # Recalculate if items changed
            line_items = []
            for idx, item_data in enumerate(update_data["items"], 1):
                line_item = calculate_line_item(POLineItemCreate(**item_data), idx)
                line_items.append(line_item)

            po.items = line_items
            po.summary = calculate_summary(line_items)

        # Update other fields
        for field, value in update_data.items():
            if field != "items" and hasattr(po, field):
                setattr(po, field, value)

        # Update tracking
        po.tracking.last_modified_by = current_user.get("email", "unknown")
        po.tracking.last_modified_date = datetime.utcnow()

        await po.save()

        return {"message": "PO updated successfully", "po_number": po.po_number}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating PO: {e}")
        raise HTTPException(500, f"Failed to update PO: {str(e)}")


@router.patch("/{po_number}/status")
async def update_po_status(
    po_number: str,
    status_data: POStatusUpdate,
    current_user = Depends(get_current_user)
):
    """Update PO status with workflow validation"""

    try:
        po = await PurchaseOrder.find_one(PurchaseOrder.po_number == po_number)

        if not po:
            raise HTTPException(404, f"Purchase Order {po_number} not found")

        # Validate status transition
        valid_transitions = {
            POStatus.DRAFT: [POStatus.SUBMITTED, POStatus.CANCELLED],
            POStatus.SUBMITTED: [POStatus.APPROVED, POStatus.CANCELLED],
            POStatus.APPROVED: [POStatus.SENT, POStatus.CANCELLED],
            POStatus.SENT: [POStatus.CONFIRMED, POStatus.CANCELLED],
            POStatus.CONFIRMED: [POStatus.PARTIALLY_RECEIVED, POStatus.RECEIVED],
            POStatus.PARTIALLY_RECEIVED: [POStatus.RECEIVED],
            POStatus.RECEIVED: [POStatus.INVOICED],
            POStatus.INVOICED: [POStatus.CLOSED],
        }

        if status_data.status not in valid_transitions.get(po.po_status, []):
            raise HTTPException(400, f"Invalid status transition from {po.po_status} to {status_data.status}")

        # Update status
        po.po_status = status_data.status

        # Update tracking timestamps
        if status_data.status == POStatus.SUBMITTED:
            po.tracking.submitted_date = datetime.utcnow()
        elif status_data.status == POStatus.APPROVED:
            po.tracking.approved_date = datetime.utcnow()
        elif status_data.status == POStatus.SENT:
            po.tracking.sent_date = datetime.utcnow()
        elif status_data.status == POStatus.CONFIRMED:
            po.tracking.confirmed_date = datetime.utcnow()
        elif status_data.status == POStatus.RECEIVED:
            po.tracking.goods_receipt_date = datetime.utcnow()
        elif status_data.status == POStatus.CLOSED:
            po.tracking.po_closed_date = datetime.utcnow()

        po.tracking.last_modified_by = current_user.get("email", "unknown")
        po.tracking.last_modified_date = datetime.utcnow()

        await po.save()

        return {"message": f"PO status updated to {status_data.status}", "po_number": po.po_number}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating PO status: {e}")
        raise HTTPException(500, f"Failed to update PO status: {str(e)}")


@router.post("/{po_number}/approve")
async def approve_purchase_order(
    po_number: str,
    approval_data: POApprovalUpdate,
    current_user = Depends(get_current_user)
):
    """Approve or reject Purchase Order"""

    try:
        po = await PurchaseOrder.find_one(PurchaseOrder.po_number == po_number)

        if not po:
            raise HTTPException(404, f"Purchase Order {po_number} not found")

        if po.po_status != POStatus.SUBMITTED:
            raise HTTPException(400, "Can only approve/reject PO in SUBMITTED status")

        # Update approval
        po.approval.approver_name = approval_data.approver_name
        po.approval.approver_email = approval_data.approver_email
        po.approval.approval_date = datetime.utcnow()
        po.approval.approval_status = approval_data.approval_status
        po.approval.approval_comments = approval_data.approval_comments

        # Update PO status
        if approval_data.approval_status == "APPROVED":
            po.po_status = POStatus.APPROVED
            po.tracking.approved_date = datetime.utcnow()
        else:
            po.po_status = POStatus.DRAFT  # Send back to draft

        po.tracking.last_modified_by = current_user.get("email", "unknown")
        po.tracking.last_modified_date = datetime.utcnow()

        await po.save()

        return {
            "message": f"PO {approval_data.approval_status.lower()}",
            "po_number": po.po_number,
            "approval_status": approval_data.approval_status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving PO: {e}")
        raise HTTPException(500, f"Failed to approve PO: {str(e)}")


@router.delete("/{po_number}")
async def delete_purchase_order(
    po_number: str,
    current_user = Depends(get_current_user)
):
    """Delete Purchase Order (only DRAFT status - soft delete)"""

    try:
        po = await PurchaseOrder.find_one(PurchaseOrder.po_number == po_number)

        if not po:
            raise HTTPException(404, f"Purchase Order {po_number} not found")

        if po.po_status != POStatus.DRAFT:
            raise HTTPException(400, "Can only delete PO in DRAFT status")

        # Soft delete
        po.is_deleted = True
        po.is_active = False
        po.tracking.last_modified_by = current_user.get("email", "unknown")
        po.tracking.last_modified_date = datetime.utcnow()

        await po.save()

        return {"message": "PO deleted successfully", "po_number": po.po_number}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting PO: {e}")
        raise HTTPException(500, f"Failed to delete PO: {str(e)}")


@router.get("/supplier/{supplier_code}")
async def get_pos_by_supplier(
    supplier_code: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get all POs for a specific supplier"""

    try:
        query = {"supplier.code": supplier_code, "is_deleted": False}

        total = await PurchaseOrder.find(query).count()
        pos = await PurchaseOrder.find(query).skip(skip).limit(limit).sort("-po_date").to_list()

        result = []
        for po in pos:
            result.append({
                "po_number": po.po_number,
                "po_date": po.po_date,
                "po_status": po.po_status,
                "grand_total": po.summary.grand_total,
                "total_items": len(po.items)
            })

        return {
            "data": result,
            "total": total,
            "supplier_code": supplier_code
        }

    except Exception as e:
        logger.error(f"Error getting POs by supplier: {e}")
        raise HTTPException(500, f"Failed to get POs: {str(e)}")


@router.get("/status/{status}")
async def get_pos_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get all POs with specific status"""

    try:
        query = {"po_status": status.upper(), "is_deleted": False}

        total = await PurchaseOrder.find(query).count()
        pos = await PurchaseOrder.find(query).skip(skip).limit(limit).sort("-po_date").to_list()

        result = []
        for po in pos:
            result.append({
                "po_number": po.po_number,
                "po_date": po.po_date,
                "supplier_name": po.supplier.name,
                "grand_total": po.summary.grand_total,
                "total_items": len(po.items)
            })

        return {
            "data": result,
            "total": total,
            "status": status
        }

    except Exception as e:
        logger.error(f"Error getting POs by status: {e}")
        raise HTTPException(500, f"Failed to get POs: {str(e)}")
