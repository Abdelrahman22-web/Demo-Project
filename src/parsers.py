"""
Spreadsheet parsing helpers and a high-level `SpreadsheetLoader`.

This module is intentionally minimal: it defines interfaces and stubs needed
by the acceptance criteria (AC-1, AC-2, AC-17). Implementations should use
an appropriate library (e.g., `pandas`, `openpyxl`, or `csv`) depending on
project constraints.
"""

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from .models import SourceReference


class ParseError(Exception):
    """Raised when a row cannot be parsed as required by AC-2.

    Implementations should attach an `error_reason` attribute describing why
    the row failed to parse (e.g., unparseable date, missing required field).
    """


class SpreadsheetLoader:
    """High-level loader that reads multiple spreadsheets and yields rows.

    Responsibilities (stubs):
    - Accept file paths (or file-like objects) representing the Production and
      Shipping logs (AC-1).
    - Normalize sheet names / provide row references for traceability (AC-17).
    - Return rows as dictionaries plus associated `SourceReference` metadata.

    Usage pattern (example):
        loader = SpreadsheetLoader()
        for row, src in loader.load_files(["prod.xlsx", "ship.csv"]):
            # row is Dict[str, Any], src is SourceReference
            ...
    """

    def __init__(self) -> None:
        # No heavy dependencies here; concrete implementations can add them.
        pass

    def load_files(
        self, paths: Iterable[str]
    ) -> Iterable[tuple[dict[str, Any], SourceReference]]:
        """Yield (row_dict, SourceReference) tuples for every row in input files.

        - `paths`: iterable of file paths to load.

        IMPORTANT: This is a stub. A production implementation should:
        - Detect file type by extension / mime
        - Stream rows to avoid excessive memory use for large spreadsheets
        - Populate `SourceReference.sheet_name` and `row_number`
        - Preserve raw string values (do not coerce types here)

        For now this function raises `NotImplementedError` to mark the work
        required for AC-1 and AC-17.
        """

        raise NotImplementedError("SpreadsheetLoader.load_files must be implemented")


def parse_date(value: str) -> datetime:
    """Parse a date-like string into a `datetime`.

    - Should accept multiple formats (AC-2) and raise `ValueError` with a
      clear message when a value is not parseable. Implementations may want
      to return `None` for empty values depending on rules.

    This stub raises NotImplementedError to indicate parsing strategy must be
    implemented by the integrator (e.g., using `dateutil.parser.parse`).
    """

    if value is None:
        raise ValueError("None is not a valid date string")

    s = str(value).strip()
    if s == "":
        raise ValueError("empty string is not a valid date")

    # Try a small, pragmatic list of common formats. This keeps dependencies
    # minimal while supporting the AC requirement to accept multiple formats.
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%b %d, %Y",  # Jan 2, 2025
        "%B %d, %Y",  # January 2, 2025
        "%d %b %Y",  # 02 Jan 2025
        "%d %B %Y",  # 2 January 2025
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]

    from datetime import datetime as _dt

    last_exc: Exception = ValueError(f"Unable to parse date: {value}")
    for fmt in formats:
        try:
            return _dt.strptime(s, fmt)
        except Exception as exc:  # noqa: BLE001 - intentional fallback
            last_exc = exc

    # As a last resort, try parsing ISO-like numeric timestamps if present
    # (e.g., Excel-style serials are out of scope here). Provide clear error.
    raise ValueError(f"Unable to parse date: {value}") from last_exc
