"""
Purchase Order Models
Complete PO system with multi-line items, calculations, and workflow
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from bson import ObjectId


class POStatus(str, Enum):
    """PO Status Enum"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    SENT = "SENT"
    CONFIRMED = "CONFIRMED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    INVOICED = "INVOICED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class PaymentTerms(str, Enum):
    """Payment Terms Enum"""
    NET_30 = "NET 30"
    NET_45 = "NET 45"
    NET_60 = "NET 60"
    COD = "COD"
    ADVANCE = "ADVANCE"
    CREDIT = "CREDIT"


class DeliveryMethod(str, Enum):
    """Delivery Method Enum"""
    FOB = "FOB"
    CIF = "CIF"
    COURIER = "COURIER"
    PICKUP = "PICKUP"


# ==================== EMBEDDED MODELS ====================

class POSupplierInfo(BaseModel):
    """Supplier information embedded in PO"""
    code: str
    name: str
    gstin: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    payment_method: str = "BANK_TRANSFER"
    payment_terms: str = "NET 30"


class POLineItem(BaseModel):
    """Line item in PO"""
    line_number: int
    item_code: str
    item_name: str
    item_description: Optional[str] = None
    item_category: Optional[str] = None
    quantity: float
    unit: str = "PCS"
    unit_rate: float
    line_amount: float  # Qty × Rate
    discount_percent: float = 0
    discount_amount: float = 0
    taxable_amount: float  # Line amount - discount
    hsn_code: Optional[str] = None
    gst_percent: float = 0
    cgst_percent: float = 0
    sgst_percent: float = 0
    igst_percent: float = 0
    gst_amount: float = 0
    cgst_amount: float = 0
    sgst_amount: float = 0
    igst_amount: float = 0
    net_amount: float  # Taxable amount + GST
    expected_delivery_date: Optional[date] = None
    inspection_required: bool = False
    quality_specs: Optional[str] = None
    notes: Optional[str] = None
    received_quantity: float = 0
    pending_quantity: float = 0


class POSummary(BaseModel):
    """PO Summary totals"""
    subtotal: float = 0  # Sum of all line amounts
    total_discount: float = 0
    total_taxable: float = 0
    total_cgst: float = 0
    total_sgst: float = 0
    total_igst: float = 0
    total_gst: float = 0
    round_off: float = 0
    grand_total: float = 0


class PODelivery(BaseModel):
    """Delivery information"""
    location: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    method: str = "COURIER"
    lead_time_days: int = 15
    expected_delivery_date: Optional[date] = None


class POPayment(BaseModel):
    """Payment information"""
    terms: str = "NET 30"
    method: str = "BANK_TRANSFER"
    currency: str = "INR"
    advance_percent: float = 0
    advance_amount: float = 0


class POApproval(BaseModel):
    """Approval information"""
    approver_name: Optional[str] = None
    approver_email: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_status: str = "PENDING"
    approval_comments: Optional[str] = None


class POTracking(BaseModel):
    """Tracking timestamps"""
    created_by: str
    created_date: datetime = Field(default_factory=datetime.utcnow)
    last_modified_by: Optional[str] = None
    last_modified_date: Optional[datetime] = None
    submitted_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    confirmed_date: Optional[datetime] = None
    goods_receipt_date: Optional[datetime] = None
    invoice_received_date: Optional[datetime] = None
    payment_made_date: Optional[datetime] = None
    po_closed_date: Optional[datetime] = None


# ==================== MAIN DOCUMENT ====================

class PurchaseOrder(Document):
    """Purchase Order Document"""

    # Header
    po_number: Indexed(str, unique=True)
    po_version: int = 1
    po_date: date
    po_status: POStatus = POStatus.DRAFT
    indent_number: Optional[str] = None

    # Supplier
    supplier: POSupplierInfo

    # Items
    items: List[POLineItem] = []

    # Summary
    summary: POSummary = Field(default_factory=POSummary)

    # Delivery
    delivery: PODelivery

    # Payment
    payment: POPayment = Field(default_factory=POPayment)

    # Additional Info
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    department: Optional[str] = None
    sample_attached: bool = False
    remarks: Optional[str] = None
    terms_and_conditions: Optional[str] = None

    # Approval
    approval: POApproval = Field(default_factory=POApproval)

    # Tracking
    tracking: POTracking

    # Attachments
    attachments: List[str] = []

    # Status
    is_active: bool = True
    is_deleted: bool = False

    class Settings:
        name = "purchase_orders"
        indexes = [
            "po_number",
            "po_status",
            "supplier.code",
            "po_date",
            "indent_number"
        ]


# ==================== REQUEST/RESPONSE SCHEMAS ====================

class POLineItemCreate(BaseModel):
    """Schema for creating/updating line item"""
    item_code: str
    item_name: str
    item_description: Optional[str] = None
    item_category: Optional[str] = None
    quantity: float
    unit: str = "PCS"
    unit_rate: float
    discount_percent: float = 0
    hsn_code: Optional[str] = None
    gst_percent: float = 0
    expected_delivery_date: Optional[date] = None
    inspection_required: bool = False
    quality_specs: Optional[str] = None
    notes: Optional[str] = None


class POCreate(BaseModel):
    """Schema for creating new PO"""
    po_date: date
    indent_number: Optional[str] = None
    supplier_code: str
    items: List[POLineItemCreate]
    delivery_location: str
    delivery_method: str = "COURIER"
    lead_time_days: int = 15
    payment_terms: str = "NET 30"
    payment_method: str = "BANK_TRANSFER"
    currency: str = "INR"
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    department: Optional[str] = None
    sample_attached: bool = False
    remarks: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class POUpdate(BaseModel):
    """Schema for updating PO"""
    po_date: Optional[date] = None
    indent_number: Optional[str] = None
    supplier_code: Optional[str] = None
    items: Optional[List[POLineItemCreate]] = None
    delivery_location: Optional[str] = None
    delivery_method: Optional[str] = None
    lead_time_days: Optional[int] = None
    payment_terms: Optional[str] = None
    payment_method: Optional[str] = None
    currency: Optional[str] = None
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    department: Optional[str] = None
    sample_attached: Optional[bool] = None
    remarks: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class POStatusUpdate(BaseModel):
    """Schema for updating PO status"""
    status: POStatus
    comments: Optional[str] = None


class POApprovalUpdate(BaseModel):
    """Schema for PO approval"""
    approver_name: str
    approver_email: str
    approval_status: str  # APPROVED or REJECTED
    approval_comments: Optional[str] = None
