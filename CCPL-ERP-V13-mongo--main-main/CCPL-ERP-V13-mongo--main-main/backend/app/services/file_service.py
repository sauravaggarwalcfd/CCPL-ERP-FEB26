"""
File Upload Service
Handles file upload, validation, storage, and image processing
"""

import os
import re
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status

logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
IMAGES_DIR = UPLOAD_DIR / "images"
THUMBNAILS_DIR = UPLOAD_DIR / "thumbnails"

# Allowed file types for images (JPEG and PNG only)
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Size limits
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
THUMBNAIL_SIZE = (200, 200)


def ensure_upload_directories():
    """Create upload directories if they don't exist"""
    UPLOAD_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)
    THUMBNAILS_DIR.mkdir(exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and special characters
    """
    # Remove directory components
    filename = os.path.basename(filename)

    # Remove special characters, keep only alphanumeric, underscore, hyphen, dot
    filename = re.sub(r'[^\w\-\.]', '_', filename)

    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    return f"{name}{ext}"


def generate_unique_filename(original_name: str) -> str:
    """
    Generate a unique filename with timestamp and UUID
    """
    sanitized = sanitize_filename(original_name)
    name, ext = os.path.splitext(sanitized)

    # Add timestamp and short UUID
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]

    return f"{name}_{timestamp}_{unique_id}{ext.lower()}"


def validate_image_file(file: UploadFile) -> Tuple[str, str]:
    """
    Validate uploaded file is an allowed image type

    Returns: (mime_type, extension)
    Raises: HTTPException if validation fails
    """
    # Check content type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{content_type}' not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES.keys())}"
        )

    # Check file extension
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' not allowed. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    else:
        ext = ALLOWED_IMAGE_TYPES[content_type]

    return content_type, ext


async def validate_file_size(file: UploadFile) -> int:
    """
    Validate file size is within limits

    Returns: file size in bytes
    Raises: HTTPException if file is too large
    """
    # Read file content to check size
    content = await file.read()
    size = len(content)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({size / 1024 / 1024:.2f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE / 1024 / 1024}MB)"
        )

    # Reset file position for later reading
    await file.seek(0)

    return size


def get_image_dimensions(file_path: Path) -> Tuple[Optional[int], Optional[int]]:
    """
    Get image dimensions

    Returns: (width, height) or (None, None) if not determinable
    """
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            return img.size
    except Exception as e:
        logger.warning(f"Could not determine image dimensions: {e}")
        return None, None


def create_thumbnail(source_path: Path, thumb_filename: str) -> Optional[str]:
    """
    Create a thumbnail for an image

    Returns: thumbnail relative path or None if failed
    """
    try:
        from PIL import Image

        thumb_path = THUMBNAILS_DIR / thumb_filename

        with Image.open(source_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Create thumbnail maintaining aspect ratio
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumb_path, "JPEG", quality=85, optimize=True)

        return f"thumbnails/{thumb_filename}"

    except ImportError:
        logger.warning("PIL not installed. Skipping thumbnail generation.")
        return None
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return None


async def save_uploaded_file(
    file: UploadFile,
    category: str = "other"
) -> dict:
    """
    Save an uploaded file to the filesystem

    Returns: dict with file info (path, url, size, dimensions, etc.)
    """
    ensure_upload_directories()

    # Validate file
    content_type, extension = validate_image_file(file)
    file_size = await validate_file_size(file)

    # Generate unique filename
    original_name = file.filename or "unnamed_file"
    unique_filename = generate_unique_filename(original_name)

    # Ensure extension is correct
    if not unique_filename.lower().endswith(extension):
        name = os.path.splitext(unique_filename)[0]
        unique_filename = f"{name}{extension}"

    # Save file
    file_path = IMAGES_DIR / unique_filename

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )

    # Get image dimensions
    width, height = get_image_dimensions(file_path)

    # Create thumbnail
    thumb_filename = f"thumb_{unique_filename.rsplit('.', 1)[0]}.jpg"
    thumbnail_path = create_thumbnail(file_path, thumb_filename)

    return {
        "file_name": unique_filename,
        "original_name": original_name,
        "file_type": content_type,
        "file_extension": extension,
        "file_size": file_size,
        "file_path": f"images/{unique_filename}",
        "file_url": f"/uploads/images/{unique_filename}",
        "thumbnail_path": thumbnail_path,
        "thumbnail_url": f"/uploads/{thumbnail_path}" if thumbnail_path else None,
        "width": width,
        "height": height,
    }


def delete_file(file_path: str, thumbnail_path: Optional[str] = None) -> bool:
    """
    Delete a file and its thumbnail from the filesystem

    Returns: True if successful, False otherwise
    """
    try:
        # Delete main file
        full_path = UPLOAD_DIR / file_path
        if full_path.exists():
            full_path.unlink()
            logger.info(f"Deleted file: {file_path}")

        # Delete thumbnail if exists
        if thumbnail_path:
            thumb_full_path = UPLOAD_DIR / thumbnail_path
            if thumb_full_path.exists():
                thumb_full_path.unlink()
                logger.info(f"Deleted thumbnail: {thumbnail_path}")

        return True

    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False


def get_file_path(relative_path: str) -> Optional[Path]:
    """
    Get the full file path from a relative path

    Returns: Path object or None if file doesn't exist
    """
    full_path = UPLOAD_DIR / relative_path
    if full_path.exists():
        return full_path
    return None


async def generate_file_id() -> str:
    """
    Generate a unique file ID in format FILE-YYYYMMDD-XXXX
    """
    from ..models.file_master import FileMaster

    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"FILE-{today}-"

    # Find the latest file ID for today
    latest_file = await FileMaster.find(
        {"file_id": {"$regex": f"^{re.escape(prefix)}"}}
    ).sort("-file_id").limit(1).to_list()

    if latest_file and len(latest_file) > 0:
        # Extract sequence number and increment
        try:
            seq = int(latest_file[0].file_id.split("-")[-1])
            next_seq = seq + 1
        except (ValueError, IndexError):
            next_seq = 1
    else:
        next_seq = 1

    return f"{prefix}{str(next_seq).zfill(4)}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024 / 1024:.2f} MB"
