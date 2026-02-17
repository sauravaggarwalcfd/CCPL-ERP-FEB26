"""
File Management API Routes
Handles file upload, listing, retrieval, and deletion
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime
import logging
import math

from ..models.file_master import (
    FileMaster,
    FileCategory,
    FileUploadResponse,
    FileListResponse,
    FileDetailResponse,
    FileUpdateRequest,
    FilePaginatedResponse,
)
from ..services.file_service import (
    save_uploaded_file,
    delete_file,
    get_file_path,
    generate_file_id,
    format_file_size,
    UPLOAD_DIR,
)
from ..core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


# ==================== FILE UPLOAD ====================

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    category: FileCategory = Query(FileCategory.OTHER),
    description: Optional[str] = Query(None),
    current_user=Depends(get_current_user)
):
    """
    Upload a new file (image)

    - Validates file type (JPEG, PNG only)
    - Validates file size (max 1MB)
    - Generates unique filename
    - Creates thumbnail for images
    - Stores metadata in database
    """
    try:
        # Save file to filesystem
        file_info = await save_uploaded_file(file, category.value)

        # Generate unique file ID
        file_id = await generate_file_id()

        # Create database record
        file_record = FileMaster(
            file_id=file_id,
            file_name=file_info["file_name"],
            original_name=file_info["original_name"],
            file_type=file_info["file_type"],
            file_extension=file_info["file_extension"],
            file_size=file_info["file_size"],
            file_path=file_info["file_path"],
            file_url=file_info["file_url"],
            thumbnail_path=file_info["thumbnail_path"],
            thumbnail_url=file_info["thumbnail_url"],
            category=category,
            description=description,
            width=file_info["width"],
            height=file_info["height"],
            uploaded_by=str(current_user.id) if current_user else None,
            uploaded_by_name=current_user.full_name if current_user else None,
        )
        await file_record.insert()

        logger.info(f"File uploaded: {file_id} - {file_info['original_name']}")

        return {
            "id": str(file_record.id),
            "file_id": file_record.file_id,
            "file_name": file_record.file_name,
            "original_name": file_record.original_name,
            "file_type": file_record.file_type,
            "file_size": file_record.file_size,
            "file_size_formatted": format_file_size(file_record.file_size),
            "file_url": file_record.file_url,
            "thumbnail_url": file_record.thumbnail_url,
            "category": file_record.category.value,
            "width": file_record.width,
            "height": file_record.height,
            "upload_date": file_record.upload_date,
            "message": "File uploaded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


# ==================== FILE LISTING ====================

@router.get("/")
async def list_files(
    category: Optional[FileCategory] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("upload_date"),
    sort_order: str = Query("desc"),
    current_user=Depends(get_current_user)
):
    """
    List all files with pagination, filtering, and search

    - Filter by category
    - Search by filename or description
    - Pagination support
    - Sort by upload_date, file_name, file_size
    """
    # Build query
    query_filters = {"is_deleted": False}

    if category:
        query_filters["category"] = category

    # Apply conditions
    query = FileMaster.find(query_filters)

    # Apply search
    if search:
        # Use $or for searching multiple fields
        query_filters["$or"] = [
            {"file_name": {"$regex": search, "$options": "i"}},
            {"original_name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
        query = FileMaster.find(query_filters)

    # Get total count
    total = await query.count()

    # Apply sorting
    sort_prefix = "-" if sort_order == "desc" else "+"
    sort_field = sort_prefix + sort_by

    # Apply pagination
    skip = (page - 1) * page_size
    files = await query.sort(sort_field).skip(skip).limit(page_size).to_list()

    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return {
        "files": [
            {
                "id": str(f.id),
                "file_id": f.file_id,
                "file_name": f.file_name,
                "original_name": f.original_name,
                "file_type": f.file_type,
                "file_size": f.file_size,
                "file_size_formatted": format_file_size(f.file_size),
                "file_url": f.file_url,
                "thumbnail_url": f.thumbnail_url,
                "category": f.category.value,
                "description": f.description,
                "width": f.width,
                "height": f.height,
                "upload_date": f.upload_date,
                "uploaded_by_name": f.uploaded_by_name,
            }
            for f in files
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ==================== FILE DETAILS ====================

@router.get("/{file_id}")
async def get_file(
    file_id: str,
    current_user=Depends(get_current_user)
):
    """Get file details by file_id"""

    file = await FileMaster.find_one({
        "file_id": file_id,
        "is_deleted": False
    })

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found"
        )

    return {
        "id": str(file.id),
        "file_id": file.file_id,
        "file_name": file.file_name,
        "original_name": file.original_name,
        "file_type": file.file_type,
        "file_extension": file.file_extension,
        "file_size": file.file_size,
        "file_size_formatted": format_file_size(file.file_size),
        "file_path": file.file_path,
        "file_url": file.file_url,
        "thumbnail_path": file.thumbnail_path,
        "thumbnail_url": file.thumbnail_url,
        "category": file.category.value,
        "description": file.description,
        "tags": file.tags,
        "width": file.width,
        "height": file.height,
        "upload_date": file.upload_date,
        "uploaded_by": file.uploaded_by,
        "uploaded_by_name": file.uploaded_by_name,
        "created_at": file.created_at,
        "updated_at": file.updated_at,
    }


# ==================== FILE DOWNLOAD/SERVE ====================

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user=Depends(get_current_user)
):
    """Download/serve a file by file_id"""

    file = await FileMaster.find_one({
        "file_id": file_id,
        "is_deleted": False
    })

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found"
        )

    # Get file path
    file_path = get_file_path(file.file_path)

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )

    return FileResponse(
        path=file_path,
        filename=file.original_name,
        media_type=file.file_type,
    )


# ==================== FILE UPDATE ====================

@router.put("/{file_id}")
async def update_file(
    file_id: str,
    data: FileUpdateRequest,
    current_user=Depends(get_current_user)
):
    """Update file metadata (category, description, tags)"""

    file = await FileMaster.find_one({
        "file_id": file_id,
        "is_deleted": False
    })

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found"
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        for field, value in update_data.items():
            setattr(file, field, value)
        await file.save()

    logger.info(f"File updated: {file_id}")

    return {
        "id": str(file.id),
        "file_id": file.file_id,
        "message": "File updated successfully"
    }


# ==================== FILE DELETE ====================

@router.delete("/{file_id}")
async def delete_file_endpoint(
    file_id: str,
    permanent: bool = Query(False),
    current_user=Depends(get_current_user)
):
    """
    Delete a file

    - By default, performs soft delete (sets is_deleted=True)
    - Use permanent=True to permanently delete file from database and disk
    """

    file = await FileMaster.find_one({
        "file_id": file_id,
        "is_deleted": False
    })

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{file_id}' not found"
        )

    if permanent:
        # Permanent delete - remove from disk and database
        delete_file(file.file_path, file.thumbnail_path)
        await file.delete()
        logger.info(f"File permanently deleted: {file_id}")
        return {"message": f"File '{file_id}' permanently deleted"}
    else:
        # Soft delete
        file.is_deleted = True
        file.deleted_at = datetime.utcnow()
        file.deleted_by = str(current_user.id) if current_user else None
        file.updated_at = datetime.utcnow()
        await file.save()
        logger.info(f"File soft deleted: {file_id}")
        return {"message": f"File '{file_id}' deleted successfully"}


# ==================== FILE SEARCH ====================

@router.get("/search/files")
async def search_files(
    q: str = Query(..., min_length=1),
    category: Optional[FileCategory] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user)
):
    """Search files by name or description"""

    query_filters = {
        "is_deleted": False,
        "$or": [
            {"file_name": {"$regex": q, "$options": "i"}},
            {"original_name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]
    }

    if category:
        query_filters["category"] = category

    files = await FileMaster.find(query_filters).limit(limit).to_list()

    return [
        {
            "id": str(f.id),
            "file_id": f.file_id,
            "file_name": f.file_name,
            "original_name": f.original_name,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "file_url": f.file_url,
            "thumbnail_url": f.thumbnail_url,
            "category": f.category.value,
        }
        for f in files
    ]


# ==================== CATEGORY STATISTICS ====================

@router.get("/stats/categories")
async def get_category_stats(
    current_user=Depends(get_current_user)
):
    """Get file count and size statistics by category"""

    stats = []

    for category in FileCategory:
        files = await FileMaster.find({
            "category": category,
            "is_deleted": False
        }).to_list()

        total_size = sum(f.file_size for f in files)

        stats.append({
            "category": category.value,
            "count": len(files),
            "total_size": total_size,
            "total_size_formatted": format_file_size(total_size),
        })

    # Get overall stats
    all_files = await FileMaster.find({"is_deleted": False}).to_list()
    total_size = sum(f.file_size for f in all_files)

    return {
        "by_category": stats,
        "total": {
            "count": len(all_files),
            "total_size": total_size,
            "total_size_formatted": format_file_size(total_size),
        }
    }


# ==================== RECENT FILES ====================

@router.get("/recent/files")
async def get_recent_files(
    limit: int = Query(10, ge=1, le=50),
    current_user=Depends(get_current_user)
):
    """Get most recently uploaded files"""

    files = await FileMaster.find({
        "is_deleted": False
    }).sort("-upload_date").limit(limit).to_list()

    return [
        {
            "id": str(f.id),
            "file_id": f.file_id,
            "file_name": f.file_name,
            "original_name": f.original_name,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "file_size_formatted": format_file_size(f.file_size),
            "file_url": f.file_url,
            "thumbnail_url": f.thumbnail_url,
            "category": f.category.value,
            "upload_date": f.upload_date,
        }
        for f in files
    ]
