"""Export utilities for weekly summary and drill-down outputs."""

import csv
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from openpyxl import Workbook

logger = logging.getLogger(__name__)


class Exporter:
    """Write tabular data to CSV and XLSX files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = Path(".") if output_dir is None else output_dir

    def export_csv(self, rows: Iterable[dict[str, Any]], filename: str) -> Path:
        rows = list(rows)
        target = self.output_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)

        headers: list[str] = []
        for row in rows:
            for key in row:
                if key not in headers:
                    headers.append(key)

        with target.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        logger.info("Exported CSV file to %s with %d rows", target, len(rows))
        return target

    def export_xlsx(
        self, tables: dict[str, Iterable[dict[str, Any]]], filename: str
    ) -> Path:
        target = self.output_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)

        workbook = Workbook()
        workbook.remove(workbook.active)

        for sheet_name, rows in tables.items():
            worksheet = workbook.create_sheet(title=str(sheet_name)[:31] or "Sheet1")
            rows = list(rows)
            if not rows:
                logger.debug(
                    "Created empty worksheet '%s' in %s", worksheet.title, target
                )
                continue

            headers: list[str] = []
            for row in rows:
                for key in row:
                    if key not in headers:
                        headers.append(key)

            worksheet.append(headers)
            for row in rows:
                worksheet.append([row.get(header) for header in headers])

        workbook.save(target)
        logger.info("Exported XLSX file to %s", target)
        return target
