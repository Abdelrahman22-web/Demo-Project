"""
Drill-down service scaffolding.

Provides APIs to fetch lots/records contributing to a ranking or category and
to enrich them with shipping status (AC-9, AC-12, AC-13, AC-14, AC-15).

Functions are stubs and document the expected behavior and return shapes.
"""

from datetime import date
from typing import Any


class DrillDownService:
    """Expose drill-down queries for production lines and categories.

    Responsibilities:
    - Given a production line, return underlying lot records and source
      references (AC-9, AC-17).
    - Given an issue category, return affected lots/records (AC-12).
    - Enrich lots with shipping status and latest ship date when available
      (AC-13, AC-14).
    - Flag "problematic but shipped" lots for UI highlighting (AC-15).
    - Detect and mark conflicts when the same canonical_lot_id shows
      inconsistent values (delegated from Consolidator or computed here)
      (AC-16).
    """

    def __init__(self) -> None:
        pass

    def drilldown_by_production_line(
        self,
        production_line: str,
        week_start: date,
        week_end: date,
        include_flagged: bool = False,
    ) -> dict[str, Any]:
        """Return drill-down rows for a production line (AC-9).

        Expected return shape (scaffold):
        {
            "production_line": production_line,
            "lots": [
                {
                    "canonical_lot_id": "LOT123",
                    "raw_lot_id": "Lot 123",
                    "source_references": [ {..SourceReference..} ],
                    "shipping_status": "Shipped",
                    "latest_ship_date": "2025-01-12",
                    "conflicts": [ ... ]
                }
            ]
        }

        This is a stub and must be implemented to fetch and enrich records.
        """

        raise NotImplementedError("drilldown_by_production_line must be implemented")

    def drilldown_by_category(
        self,
        category: str,
        week_start: date,
        week_end: date,
        include_comparison: bool = False,
    ) -> dict[str, Any]:
        """Return drill-down rows for an issue/defect category (AC-12).

        If `include_comparison` is True, include rows from the comparison
        period to help analysts inspect trending differences.
        """

        raise NotImplementedError("drilldown_by_category must be implemented")
