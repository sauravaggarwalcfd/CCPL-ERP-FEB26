"""Pydantic models for BOM (Dyeing Bill of Materials) module.
These are pure Pydantic models (not Beanie Documents) since BOM data
is stored in Google Sheets, not MongoDB.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ MASTER DATA MODELS ============

class Article(BaseModel):
    """Article summary from sheet tabs."""
    sheet_name: str
    art_no: str
    set_no: str = ""
    season: str = ""
    plan_qty: float = 0
    buyer: str = ""
    plan_date: str = ""
    remarks: str = ""


class MasterArticle(BaseModel):
    """Article from MASTER DATA sheet."""
    art_no: str
    sketch_link: str = ""


class Color(BaseModel):
    """Color from MASTER DATA sheet."""
    id: str = ""
    code: str = ""
    name: str


class FabricQuality(BaseModel):
    """Fabric quality from FABRIC MASTERDATA sheet."""
    quality: str
    unit: str = "kg"
    avg_roll_size: float = 25


class MasterData(BaseModel):
    """All master data combined."""
    articles: List[Article] = []
    colors: List[Color] = []
    components: List[str] = []
    units: List[str] = ["kg", "Pcs", "Meter", "Cuts"]
    master_articles: List[MasterArticle] = []
    fabrics: List[FabricQuality] = []


# ============ BOM MODELS ============

class BOMLine(BaseModel):
    """Single BOM line item."""
    fabric_quality: str = ""
    fc_no: str = ""
    plan_rat_gsm: str = ""
    priority: str = ""
    component: str = ""
    avg: float = 0
    unit: str = "kg"
    extra_pcs: float = 0
    wastage_pcs: float = 0
    shortage: float = 0
    ready_fabric_need: float = 0
    greige_fabric_need: float = 0
    no_of_rolls: Optional[float] = None
    greige_is_manual: bool = False


class Combo(BaseModel):
    """Color combo with BOM lines."""
    combo_sr_no: int = 1
    combo_name: str = ""
    lot_no: str = ""
    lot_count: int = 1
    color_id: str = ""
    color_code: str = ""
    color_name: str = ""
    plan_qty: float = 0
    bom_lines: List[BOMLine] = []


class BOMHeader(BaseModel):
    """BOM header information."""
    uid: Optional[str] = None
    art_no: str = ""
    set_no: str = ""
    season: str = ""
    buyer: str = ""
    plan_date: str = ""
    plan_qty: float = 0
    remarks: str = ""
    combo_count: int = 0
    line_count: int = 0
    status: str = "UNALLOCATED"
    dplan_no: str = ""
    sheet_name: str = ""
    created_at: str = ""
    updated_at: str = ""
    created_by: str = ""


class BOM(BaseModel):
    """Full BOM with header and combos."""
    header: BOMHeader
    combos: List[Combo] = []


class BOMSaveRequest(BaseModel):
    """Request to save a BOM."""
    uid: Optional[str] = None
    header: BOMHeader
    combos: List[Combo]


class BOMIndexItem(BaseModel):
    """BOM summary for index listing."""
    uid: str
    art_no: str
    set_no: str = ""
    season: str = ""
    buyer: str = ""
    plan_date: str = ""
    plan_qty: float = 0
    remarks: str = ""
    combo_count: int = 0
    line_count: int = 0
    status: str = "UNALLOCATED"
    dplan_no: str = ""
    sheet_name: str = ""
    created_at: str = ""
    updated_at: str = ""
    created_by: str = ""


class BOMIndexFilter(BaseModel):
    """Filter for BOM index queries."""
    status: Optional[str] = None
    dplan_no: Optional[str] = None


# ============ DYEING PLAN MODELS ============

class DyeingPlan(BaseModel):
    """Dyeing plan summary."""
    dplan_no: str
    bom_count: int = 0
    total_qty: float = 0
    created_at: str = ""
    created_by: str = ""
    notes: str = ""


class AllocateRequest(BaseModel):
    """Request to allocate BOMs to a dyeing plan."""
    uids: List[str]
    dplan_no: str


# ============ RESPONSE MODELS ============

class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str = ""


class SaveBOMResponse(BaseModel):
    """Response from saving a BOM."""
    success: bool
    uid: Optional[str] = None
    message: str = ""
    tab_result: Optional[dict] = None


class AllocateResponse(BaseModel):
    """Response from allocating BOMs."""
    success: bool
    allocated: int = 0
    dplan_no: str = ""
    message: str = ""


class ImportResponse(BaseModel):
    """Response from auto-importing BOMs."""
    imported: int = 0
    skipped: int = 0
    errors: int = 0
    items: List[BOMIndexItem] = []
