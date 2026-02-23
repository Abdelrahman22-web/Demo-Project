"""
Weekly summary generation scaffolding.

This module provides `WeeklySummaryGenerator`, a stubbed service whose
responsibilities map to AC-6 through AC-9 and AC-18 (export). The generator
should be given consolidated, canonicalized rows (e.g., output of
`Consolidator.consolidate`) and compute ranking by production line.
"""

from datetime import date
from typing import Any


class WeeklySummaryGenerator:
    """Generates weekly rankings and exposes drill-down keys.

    Responsibilities:
    - Accept a canonical dataset (list of rows with `run_date`,
      `production_line`, `line_issue_flag`).
    - Apply a week-window filter (AC-7). Implementers should choose a
      consistent week definition (e.g., Monday-Sunday) and document it.
    - Compute issue counts according to a configurable rule and provide the
      rule text for UI display (AC-6).
    - Produce an ordered ranking (descending by issue count) with totals
      per production line (AC-8).
    - Provide the ability to return drill-down keys (production line -> list
      of lot ids or row references) for AC-9.
    """

    def __init__(
        self, *, issue_rule_description: str = "line_issue_flag == True"
    ) -> None:
        # Human-readable description of how an "issue" is determined (AC-6)
        self.issue_rule_description = issue_rule_description

    def generate(
        self, canonical_rows: list[dict[str, Any]], week_start: date, week_end: date
    ) -> dict[str, Any]:
        """Return a summary dict containing ranking + metadata.

        Return structure suggestion (scaffold):
        {
            "week": {"start": week_start, "end": week_end},
            "issue_rule": self.issue_rule_description,
            "ranking": [
                {"production_line": "Line A", "issue_count": 10, "total_runs": 20}
            ],
            "drilldown_map": {"Line A": ["LOT123", "LOT456"]}
        }

        This method is a stub and must be implemented to compute counts and
        order results (AC-8).
        """

        raise NotImplementedError("WeeklySummaryGenerator.generate must be implemented")
