"""Expression filter support for SheetDocument.
Enables Beanie-style queries like: User.email == "admin@ccpl.com"
"""
import re
from typing import Any, Callable, Dict, List, Optional


class FilterExpr:
    """Represents a single filter condition."""
    __slots__ = ('field', 'op', 'value')

    def __init__(self, field: str, op: str, value: Any):
        self.field = field
        self.op = op
        self.value = value

    def match(self, row: Dict) -> bool:
        val = row.get(self.field, '')
        if self.op == 'eq':
            if self.value is None:
                return val == '' or val is None or val == 'None'
            return str(val) == str(self.value)
        elif self.op == 'ne':
            if self.value is None:
                return val != '' and val is not None and val != 'None'
            return str(val) != str(self.value)
        elif self.op == 'lt':
            try: return float(val) < float(self.value)
            except (ValueError, TypeError): return str(val) < str(self.value)
        elif self.op == 'gt':
            try: return float(val) > float(self.value)
            except (ValueError, TypeError): return str(val) > str(self.value)
        elif self.op == 'lte':
            try: return float(val) <= float(self.value)
            except (ValueError, TypeError): return str(val) <= str(self.value)
        elif self.op == 'gte':
            try: return float(val) >= float(self.value)
            except (ValueError, TypeError): return str(val) >= str(self.value)
        elif self.op == 'startswith':
            return str(val).startswith(str(self.value))
        elif self.op == 'regex':
            flags = re.IGNORECASE if self.value.get('flags') else 0
            return bool(re.search(self.value['pattern'], str(val), flags))
        return False


class FieldProxy:
    """Proxy for model class attributes that captures comparison operations."""
    __slots__ = ('field_name',)

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __eq__(self, other):
        return FilterExpr(self.field_name, 'eq', other)

    def __ne__(self, other):
        return FilterExpr(self.field_name, 'ne', other)

    def __lt__(self, other):
        return FilterExpr(self.field_name, 'lt', other)

    def __gt__(self, other):
        return FilterExpr(self.field_name, 'gt', other)

    def __le__(self, other):
        return FilterExpr(self.field_name, 'lte', other)

    def __ge__(self, other):
        return FilterExpr(self.field_name, 'gte', other)

    def startswith(self, prefix):
        return FilterExpr(self.field_name, 'startswith', prefix)

    def __hash__(self):
        return hash(self.field_name)


def parse_dict_query(query: Dict) -> Callable:
    """Parse a MongoDB-style dict query into a filter function."""
    def _match(row: Dict) -> bool:
        for key, value in query.items():
            if key == '$or':
                sub_fns = [parse_dict_query(sq) for sq in value]
                if not any(fn(row) for fn in sub_fns):
                    return False
                continue

            # Handle FieldProxy keys
            field_name = key.field_name if isinstance(key, FieldProxy) else str(key)
            cell_val = row.get(field_name, '')

            if isinstance(value, dict):
                # MongoDB operators
                if '$regex' in value:
                    pattern = value['$regex']
                    flags = re.IGNORECASE if value.get('$options') == 'i' else 0
                    if not re.search(pattern, str(cell_val), flags):
                        return False
                if '$gte' in value:
                    try:
                        if not (float(cell_val) >= float(value['$gte'])):
                            return False
                    except (ValueError, TypeError):
                        if not (str(cell_val) >= str(value['$gte'])):
                            return False
                if '$lte' in value:
                    try:
                        if not (float(cell_val) <= float(value['$lte'])):
                            return False
                    except (ValueError, TypeError):
                        if not (str(cell_val) <= str(value['$lte'])):
                            return False
                if '$gt' in value:
                    try:
                        if not (float(cell_val) > float(value['$gt'])):
                            return False
                    except (ValueError, TypeError):
                        return False
                if '$lt' in value:
                    try:
                        if not (float(cell_val) < float(value['$lt'])):
                            return False
                    except (ValueError, TypeError):
                        return False
            elif isinstance(value, FilterExpr):
                if not value.match(row):
                    return False
            else:
                # Simple equality
                if value is None:
                    if cell_val != '' and cell_val is not None and cell_val != 'None':
                        return False
                else:
                    if str(cell_val) != str(value):
                        return False
        return True
    return _match


def build_filter_from_args(args) -> Optional[Callable]:
    """Build a filter function from *args passed to find()/find_one().
    Supports: FilterExpr objects, dict queries, or mixed.
    """
    if not args:
        return None

    filters = []
    for arg in args:
        if isinstance(arg, FilterExpr):
            filters.append(arg.match)
        elif isinstance(arg, dict):
            filters.append(parse_dict_query(arg))
        elif callable(arg):
            filters.append(arg)

    if not filters:
        return None

    def combined(row):
        return all(f(row) for f in filters)
    return combined
