"""I/O helpers for reading production and shipping spreadsheets.

This module centralizes file parsing so the rest of the code can operate on
DataFrames with predictable schemas.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize spreadsheet column names into snake_case-like labels.

    Complexity:
    - Time: O(c * k), where c is number of columns and k average name length.
    - Space: O(c) for the new column list.
    """

    normalized = []
    for col in df.columns:
        cleaned = str(col).strip().lower().replace(" ", "_").replace("/", "_")
        normalized.append(cleaned)
    df = df.copy()
    df.columns = normalized
    return df


def _read_spreadsheet(path: str | Path, sheet_name: str | None = None) -> pd.DataFrame:
    """Read a CSV or XLSX file and return a DataFrame.

    Complexity:
    - Time: O(r * c), proportional to file size.
    - Space: O(r * c) to hold loaded table in memory.
    """

    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
        return _normalize_columns(df)
    if suffix in {".xlsx", ".xls"}:
        # Pandas closes the file handle internally after read completion.
        df = pd.read_excel(path, sheet_name=sheet_name or 0)
        return _normalize_columns(df)
    raise ValueError(f"Unsupported file extension: {suffix}")


def load_production_file(path: str | Path, sheet_name: str | None = None) -> pd.DataFrame:
    """Load production spreadsheet and append source traceability columns.

    Complexity:
    - Time: O(r * c) file read + O(r) metadata assignments.
    - Space: O(r * c).
    """

    df = _read_spreadsheet(path, sheet_name=sheet_name)
    file_name = Path(path).name
    # Source details are required for AC-17 traceability.
    df["source_file"] = file_name
    df["source_sheet"] = sheet_name or "Sheet1"
    # Spreadsheet row references are 1-based with header at row 1.
    df["source_row"] = (df.index + 2).astype(int)
    return df


def load_shipping_file(path: str | Path, sheet_name: str | None = None) -> pd.DataFrame:
    """Load shipping spreadsheet and append source traceability columns.

    Complexity:
    - Time: O(r * c) file read + O(r) metadata assignments.
    - Space: O(r * c).
    """

    df = _read_spreadsheet(path, sheet_name=sheet_name)
    file_name = Path(path).name
    df["source_file"] = file_name
    df["source_sheet"] = sheet_name or "Sheet1"
    df["source_row"] = (df.index + 2).astype(int)
    return df
