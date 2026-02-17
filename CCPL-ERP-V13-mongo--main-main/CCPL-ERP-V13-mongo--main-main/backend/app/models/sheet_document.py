"""SheetDocument — Drop-in replacement for Beanie Document backed by Google Sheets.
Provides the same API surface: find(), find_one(), get(), save(), insert(), delete().
"""
import json
import uuid
import logging
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, get_origin, get_args, Type

from pydantic import BaseModel, Field

from .sheet_expressions import FilterExpr, FieldProxy, build_filter_from_args
from .sheet_query import SheetQuery

logger = logging.getLogger(__name__)


class SheetDocumentMeta(type(BaseModel)):
    """Metaclass that returns FieldProxy when class attributes are accessed for filtering."""

    def __getattr__(cls, name: str):
        # Return FieldProxy for model fields (used in expressions like User.email == ...)
        if name.startswith('_') or name in ('model_fields', 'model_config', 'SheetSettings',
                                             '__annotations__', '__class__', '__dict__',
                                             '__pydantic_complete__', '__pydantic_core_schema__',
                                             '__pydantic_serializer__', '__pydantic_validator__',
                                             '__pydantic_decorators__', '__pydantic_parent_namespace__',
                                             '__pydantic_generic_metadata__'):
            raise AttributeError(name)
        # Check if it's a model field
        if hasattr(cls, 'model_fields') and name in cls.model_fields:
            return FieldProxy(name)
        raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")


class SheetDocument(BaseModel, metaclass=SheetDocumentMeta):
    """Base class for all models. Replaces beanie.Document."""

    id: Optional[str] = Field(default=None, alias='_id')

    model_config = {'populate_by_name': True, 'arbitrary_types_allowed': True}

    class SheetSettings:
        tab_name: str = ""
        unique_fields: list = []

    # ==================== CLASS METHODS ====================

    @classmethod
    def _get_db(cls):
        from ..services.sheets_db_service import get_sheets_db
        return get_sheets_db()

    @classmethod
    def _get_tab(cls) -> str:
        return cls.SheetSettings.tab_name

    @classmethod
    def _get_headers(cls) -> List[str]:
        """Get column headers from model fields."""
        headers = ['_id']
        for name in cls.model_fields:
            if name != 'id' and name not in headers:
                headers.append(name)
        return headers

    @classmethod
    def _from_row(cls, row: Dict[str, Any]) -> "SheetDocument":
        """Deserialize a sheet row dict into a model instance."""
        data = {}
        for field_name, field_info in cls.model_fields.items():
            if field_name == 'id':
                # Use field name 'id' (not alias '_id') so Pydantic finds it
                data['id'] = row.get('_id', '')
                continue

            raw = row.get(field_name, '')
            if raw == '' or raw is None:
                data[field_name] = None
                continue

            annotation = field_info.annotation
            data[field_name] = _deserialize_value(raw, annotation)

        try:
            return cls.model_validate(data)
        except Exception as e:
            logger.debug(f"Deserialization issue for {cls.__name__}: {e}")
            # Fallback: map _id to id for Pydantic
            fallback = dict(row)
            if '_id' in fallback:
                fallback['id'] = fallback.pop('_id')
            return cls.model_validate(fallback)

    def _to_row(self) -> Dict[str, str]:
        """Serialize model instance to a sheet row dict."""
        row = {}
        row['_id'] = self.id or ''

        for field_name, field_info in self.model_fields.items():
            if field_name == 'id':
                continue
            value = getattr(self, field_name, None)
            row[field_name] = _serialize_value(value)

        return row

    @classmethod
    async def find_one(cls, *args, **kwargs) -> Optional["SheetDocument"]:
        """Find a single document matching filters."""
        db = cls._get_db()
        filter_fn = build_filter_from_args(args)
        if filter_fn is None:
            # No filter, return first
            rows = db.find(cls._get_tab())
            return cls._from_row(rows[0]) if rows else None

        row = db.find_one(cls._get_tab(), filter_fn)
        return cls._from_row(row) if row else None

    @classmethod
    def find(cls, *args, **kwargs) -> SheetQuery:
        """Find documents matching filters. Returns a chainable SheetQuery."""
        db = cls._get_db()
        filter_fn = build_filter_from_args(args)
        rows = db.find(cls._get_tab(), filter_fn)
        return SheetQuery(cls, rows)

    @classmethod
    async def find_all(cls) -> SheetQuery:
        """Return all documents."""
        db = cls._get_db()
        rows = db.find(cls._get_tab())
        return SheetQuery(cls, rows)

    @classmethod
    async def get(cls, doc_id, **kwargs) -> Optional["SheetDocument"]:
        """Get document by _id."""
        db = cls._get_db()
        row = db.get_by_id(cls._get_tab(), str(doc_id))
        return cls._from_row(row) if row else None

    # ==================== INSTANCE METHODS ====================

    async def save(self) -> "SheetDocument":
        """Save (insert or update) the document."""
        db = self._get_db()

        if not self.id:
            self.id = uuid.uuid4().hex

        row = self._to_row()

        # Check if exists
        existing = db.get_by_id(self._get_tab(), self.id)
        if existing:
            db.update(self._get_tab(), self.id, row)
        else:
            db.insert(self._get_tab(), row)

        return self

    async def insert(self) -> "SheetDocument":
        """Insert as new document."""
        db = self._get_db()

        if not self.id:
            self.id = uuid.uuid4().hex

        row = self._to_row()
        db.insert(self._get_tab(), row)
        return self

    async def delete(self) -> None:
        """Delete this document."""
        if self.id:
            db = self._get_db()
            db.delete(self._get_tab(), self.id)

    async def set(self, fields: Dict[str, Any]) -> None:
        """Update specific fields (like Beanie's .set())."""
        for key, value in fields.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await self.save()

    def dict(self, **kwargs) -> dict:
        """Override dict() for backward compat."""
        return self.model_dump(**kwargs)


# ==================== SERIALIZATION HELPERS ====================

def _serialize_value(value: Any) -> str:
    """Serialize a Python value to a sheet cell string."""
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(), default=str)
    if isinstance(value, list):
        if not value:
            return '[]'
        if isinstance(value[0], BaseModel):
            return json.dumps([item.model_dump() for item in value], default=str)
        return json.dumps(value, default=str)
    if isinstance(value, dict):
        return json.dumps(value, default=str)
    return str(value)


def _deserialize_value(raw: str, annotation: Any) -> Any:
    """Deserialize a sheet cell string back to a Python value."""
    if raw == '' or raw is None:
        return None

    # Unwrap Optional
    origin = get_origin(annotation)
    if origin is type(None):
        return None

    # Handle Optional[X] -> extract X
    args = get_args(annotation)
    if args and type(None) in args:
        # Optional type - get the non-None arg
        inner_types = [a for a in args if a is not type(None)]
        if inner_types:
            annotation = inner_types[0]
            origin = get_origin(annotation)
            args = get_args(annotation)

    # Handle List[X]
    if origin is list:
        inner_args = get_args(annotation)
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            if inner_args and isinstance(inner_args[0], type) and issubclass(inner_args[0], BaseModel):
                return [inner_args[0].model_validate(item) if isinstance(item, dict) else item for item in data]
            return data
        except (json.JSONDecodeError, TypeError):
            return []

    # Handle BaseModel subclasses
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            return annotation.model_validate(data) if isinstance(data, dict) else None
        except (json.JSONDecodeError, TypeError, Exception):
            return None

    # Handle Enum subclasses
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        try:
            return annotation(raw)
        except (ValueError, KeyError):
            return raw

    # Handle datetime
    if annotation is datetime:
        try:
            return datetime.fromisoformat(str(raw))
        except (ValueError, TypeError):
            return None

    # Handle bool
    if annotation is bool:
        if isinstance(raw, bool):
            return raw
        return str(raw).lower() in ('true', '1', 'yes')

    # Handle int
    if annotation is int:
        try:
            return int(float(raw))
        except (ValueError, TypeError):
            return 0

    # Handle float
    if annotation is float:
        try:
            return float(raw)
        except (ValueError, TypeError):
            return 0.0

    # Handle dict
    if annotation is dict or origin is dict:
        try:
            return json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, TypeError):
            return {}

    # Default: return as string
    return raw
