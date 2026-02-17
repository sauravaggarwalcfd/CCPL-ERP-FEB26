"""
Dyeing BOM API Routes
Google Sheets-backed BOM management for dyeing fabric planning.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
import logging

from ..models.bom import (
    MasterData, BOM, BOMSaveRequest, BOMIndexItem,
    DyeingPlan, AllocateRequest, AllocateResponse,
    SaveBOMResponse, ImportResponse, FabricQuality
)
from ..services.bom_sheets_service import get_sheets_service, SheetsService
from ..core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def get_service() -> SheetsService:
    """Dependency to get sheets service."""
    return get_sheets_service()


# ============ STATUS ============

@router.get("/status")
async def get_bom_status(
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Get BOM module status (demo mode info)."""
    return {
        "status": "ok",
        "demo_mode": service.demo_mode,
        "message": service.error_message if service.demo_mode else "Connected to Google Sheets",
        "spreadsheet_configured": not service.demo_mode,
    }


# ============ MASTER DATA ============

@router.get("/master-data", response_model=MasterData)
async def get_bom_master_data(
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Load all BOM master data (articles, colors, components, fabrics)."""
    try:
        return service.load_all_master_data()
    except Exception as e:
        logger.error(f"Error loading BOM master data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fabrics", response_model=List[FabricQuality])
async def get_bom_fabrics(
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Get all fabric qualities."""
    try:
        return service.get_fabric_qualities()
    except Exception as e:
        logger.error(f"Error loading fabrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ARTICLES ============

@router.get("/articles/{sheet_name}/bom", response_model=BOM)
async def get_article_bom(
    sheet_name: str,
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Load BOM data from an article sheet."""
    try:
        return service.load_article_bom(sheet_name)
    except Exception as e:
        logger.error(f"Error loading article BOM: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/articles")
async def create_article(
    art_no: str,
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Create a new article sheet from DUMMY template."""
    try:
        result = service.create_new_article_sheet(art_no)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ BOM CRUD ============

@router.post("/", response_model=SaveBOMResponse)
async def save_bom(
    request: BOMSaveRequest,
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Save a BOM (create or update)."""
    try:
        result = service.save_bom_full(request.uid, request.header, request.combos)
        return SaveBOMResponse(**result)
    except Exception as e:
        logger.error(f"Error saving BOM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[BOMIndexItem])
async def list_boms(
    status: Optional[str] = None,
    dplan_no: Optional[str] = None,
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """List BOMs with optional filtering."""
    try:
        return service.load_bom_index(status=status, dplan_no=dplan_no)
    except Exception as e:
        logger.error(f"Error listing BOMs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{uid}", response_model=BOM)
async def get_bom(
    uid: str,
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Load a BOM by UID."""
    try:
        return service.load_bom_by_uid(uid)
    except Exception as e:
        logger.error(f"Error loading BOM {uid}: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/import", response_model=ImportResponse)
async def import_boms(
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Auto-import all existing article BOMs into the database."""
    try:
        result = service.auto_import_all_boms()
        return ImportResponse(**result)
    except Exception as e:
        logger.error(f"Error importing BOMs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ALLOCATION ============

@router.post("/allocate", response_model=AllocateResponse)
async def allocate_boms(
    request: AllocateRequest,
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Allocate BOMs to a Dyeing Plan."""
    try:
        result = service.allocate_boms(request.uids, request.dplan_no)
        return AllocateResponse(**result)
    except Exception as e:
        logger.error(f"Error allocating BOMs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unallocate")
async def unallocate_boms(
    uids: List[str],
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Unallocate BOMs from their Dyeing Plans."""
    try:
        return service.unallocate_boms(uids)
    except Exception as e:
        logger.error(f"Error unallocating BOMs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ DYEING PLANS ============

@router.get("/plans", response_model=List[DyeingPlan])
async def get_plans(
    service: SheetsService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    """Get all Dyeing Plans."""
    try:
        return service.load_dplans()
    except Exception as e:
        logger.error(f"Error loading plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))
