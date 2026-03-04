"""
Export utilities for weekly summary and drill-down exports (AC-18, AC-19).

This module exposes an `Exporter` class with method stubs for exporting to
CSV/XLSX. Implementations should use a library like `csv` for CSV and
`openpyxl`/`xlsxwriter` for XLSX.
"""

from collections.abc import Iterable
from pathlib import Path
from typing import Any


class Exporter:
    """Simple export interface.

    Responsibilities:
    - Export ranking + trending tables including metadata (week range, timestamp)
      (AC-18).
    - Export drill-down result rows including shipping status fields used to
      answer "has it shipped?" (AC-19).
    - Return the path to the generated file and/or a bytes buffer.
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = Path(".") if output_dir is None else output_dir

    def export_csv(self, rows: Iterable[dict[str, Any]], filename: str) -> Path:
        """Export `rows` to CSV at `filename` inside `output_dir`.

        This is a stub; real implementations should ensure proper escaping,
        consistent column ordering, and include metadata rows when required.
        """

        raise NotImplementedError("Exporter.export_csv must be implemented")

    def export_xlsx(
        self, tables: dict[str, Iterable[dict[str, Any]]], filename: str
    ) -> Path:
        """Export multiple named tables to a single XLSX file.

        - `tables`: mapping from sheet name -> iterable of row dicts.
        - `filename`: target filename (no path). Returns the full Path.
        """

        raise NotImplementedError("Exporter.export_xlsx must be implemented")
