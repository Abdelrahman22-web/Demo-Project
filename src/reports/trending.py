"""
Trending calculations scaffolding.

This module contains `TrendingCalculator` which compares the selected week
to a previous period (default: previous week) and returns counts + deltas
required by AC-10 and AC-11. It also provides drill-down keys for AC-12.
"""

from datetime import date
from typing import Any


class TrendingCalculator:
    """Compute category-level counts and week-over-week deltas.

    Responsibilities:
    - Accept canonical rows that include an `issue_category` field.
    - Group by category and count occurrences for the selected week and
      comparison period (default previous week).
    - Return structured counts + delta (absolute and direction) for UI.
    - Provide drill-down mapping from a category to affected lots/rows.
    """

    def __init__(self) -> None:
        pass

    def compute(
        self,
        canonical_rows: list[dict[str, Any]],
        week_start: date,
        week_end: date,
        prev_start: date,
        prev_end: date,
    ) -> dict[str, Any]:
        """Return a structure describing current counts, previous counts, and deltas.

        Suggested return scaffold:
        {
            "week": {"start": week_start, "end": week_end},
            "comparison": {"start": prev_start, "end": prev_end},
            "categories": [
                {
                    "category": "Scratch",
                    "current_count": 12,
                    "previous_count": 5,
                    "delta": 7,
                    "direction": "up",
                    "drilldown_lots": ["LOT1", "LOT2"],
                }
            ]
        }

        This method is a stub and must be implemented to compute grouping and
        deltas per AC-11.
        """

        raise NotImplementedError("TrendingCalculator.compute must be implemented")
