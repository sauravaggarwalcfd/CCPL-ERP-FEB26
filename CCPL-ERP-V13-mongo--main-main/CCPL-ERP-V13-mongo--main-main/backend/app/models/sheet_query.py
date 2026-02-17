"""Chainable query builder for SheetDocument.
Supports: .skip(n).limit(m).sort(field).to_list() and .count()
"""
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class SheetQuery:
    """Mimics Beanie's query chaining: find().skip().limit().sort().to_list()"""

    def __init__(self, model_class, results: List[dict]):
        self._model_class = model_class
        self._results = results
        self._skip_n = 0
        self._limit_n = None
        self._sort_field = None
        self._sort_reverse = False

    def skip(self, n: int) -> "SheetQuery":
        self._skip_n = n
        return self

    def limit(self, n: int) -> "SheetQuery":
        self._limit_n = n
        return self

    def sort(self, field: str) -> "SheetQuery":
        if field.startswith('-'):
            self._sort_field = field[1:]
            self._sort_reverse = True
        elif field.startswith('+'):
            self._sort_field = field[1:]
            self._sort_reverse = False
        else:
            self._sort_field = field
            self._sort_reverse = False
        return self

    def _apply(self) -> list:
        """Apply sort, skip, limit to results."""
        data = list(self._results)

        if self._sort_field:
            def sort_key(row):
                val = row.get(self._sort_field, '')
                if val == '' or val is None:
                    return ''
                # Try numeric sort
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return str(val)
            data.sort(key=sort_key, reverse=self._sort_reverse)

        if self._skip_n:
            data = data[self._skip_n:]

        if self._limit_n is not None:
            data = data[:self._limit_n]

        return data

    async def to_list(self) -> list:
        """Execute query and return list of model instances."""
        data = self._apply()
        return [self._model_class._from_row(row) for row in data]

    async def count(self) -> int:
        """Count matching results (ignores skip/limit)."""
        return len(self._results)
