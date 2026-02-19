"""Normalization and parsing helpers for raw spreadsheet fields.

The functions in this module are pure and deterministic, which keeps them easy
to test and safe to reuse across import pipelines.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd


# Precompiled regex improves repeated parsing performance by avoiding
# recompilation overhead in row-by-row normalization loops.
LOT_PATTERN = re.compile(r"LOT[-_ ]?(\d{8})[-_ ]?(\d{3})")


@dataclass(slots=True)
class LotNormalization:
    """Result object for lot normalization.

    Complexity:
    - Time: O(1) per normalization call (bounded regex/string operations).
    - Space: O(1).
    """

    canonical_lot_id: str | None
    status: str
    reason: str | None


def parse_mixed_date(value: object) -> tuple[pd.Timestamp | pd.NaT, str | None]:
    """Parse mixed-format date values into a concrete pandas Timestamp.

    Returns a tuple of parsed value and optional error reason.

    Complexity:
    - Time: O(k), where k is input string length for parser work.
    - Space: O(1) additional storage.
    """

    if value is None or (isinstance(value, float) and pd.isna(value)):
        # Return explicit reason so callers can show users why a row was flagged.
        return pd.NaT, "Date is empty"

    # Pandas handles multiple formats and timestamp-like values robustly.
    parsed = pd.to_datetime(value, errors="coerce", utc=False)
    if pd.isna(parsed):
        return pd.NaT, f"Unparseable date value: {value!r}"
    return parsed.normalize(), None


def normalize_lot_id(raw_lot_id: object) -> LotNormalization:
    """Normalize a raw lot identifier to canonical format `LOT-YYYYMMDD-XXX`.

    Rules:
    - Trim whitespace.
    - Uppercase text.
    - Replace common typo prefix `L0T` -> `LOT`.
    - Allow spaces/underscores/hyphens.
    - Reject values that do not fit expected pattern.

    Complexity:
    - Time: O(n), where n is lot string length.
    - Space: O(n) for normalized intermediate strings.
    """

    if raw_lot_id is None or (isinstance(raw_lot_id, float) and pd.isna(raw_lot_id)):
        return LotNormalization(None, "needs_review", "Lot ID is empty")

    # Normalize casing and strip leading/trailing whitespace noise.
    raw_text = str(raw_lot_id).strip().upper()
    if not raw_text:
        return LotNormalization(None, "needs_review", "Lot ID is blank")

    # Common typo correction: zero used instead of letter O in LOT prefix.
    corrected = raw_text.replace("L0T", "LOT")
    # Remove separators so compact forms like LOT20260101001 can be handled.
    compact = re.sub(r"[\s\-_]+", "", corrected)
    # Reinsert expected structure for pattern matching.
    structured = re.sub(r"^LOT(\d{8})(\d{3})$", r"LOT-\1-\2", compact)
    match = LOT_PATTERN.search(structured)
    if not match:
        return LotNormalization(None, "needs_review", f"Lot ID does not match expected pattern: {raw_lot_id!r}")

    canonical = f"LOT-{match.group(1)}-{match.group(2)}"
    return LotNormalization(canonical, "ok", None)


def truthy_issue_flag(value: object) -> bool:
    """Convert mixed indicator values into a boolean issue flag.

    Accepted truthy values include Yes/True/1/Y/T (case-insensitive).

    Complexity:
    - Time: O(m), where m is string length for normalized comparisons.
    - Space: O(1).
    """

    if isinstance(value, bool):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    normalized = str(value).strip().lower()
    return normalized in {"yes", "y", "true", "t", "1"}
