"""Export helpers for weekly summary and drill-down datasets."""

from __future__ import annotations

import io
from datetime import datetime, timezone

import pandas as pd

from ops_dashboard.models import WeeklySummaryResult


def export_weekly_summary_csv(summary: WeeklySummaryResult) -> bytes:
    """Export ranking + trending tables to a single CSV payload.

    The function emits a metadata block followed by two tables so files remain
    spreadsheet-friendly while still carrying context.

    Complexity:
    - Time: O(r + t), where r is ranking rows and t is trending rows.
    - Space: O(r + t) for serialized text buffer.
    """

    timestamp = datetime.now(timezone.utc).isoformat()
    buffer = io.StringIO()
    buffer.write(f"week_start,{summary.week_start.date()}\n")
    buffer.write(f"week_end,{summary.week_end.date()}\n")
    buffer.write(f"generated_utc,{timestamp}\n\n")
    buffer.write("ranking_table\n")
    summary.ranking.to_csv(buffer, index=False)
    buffer.write("\ntrending_table\n")
    summary.trending.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def export_weekly_summary_xlsx(summary: WeeklySummaryResult) -> bytes:
    """Export weekly summary tables to XLSX bytes.

    Resource handling:
    - `ExcelWriter` is managed by a context manager, ensuring file resources are
      closed deterministically even when exceptions occur.

    Complexity:
    - Time: O(r + t) for dataframe writes.
    - Space: O(r + t) within the in-memory workbook buffer.
    """

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        metadata = pd.DataFrame(
            {
                "field": ["week_start", "week_end", "generated_utc"],
                "value": [
                    str(summary.week_start.date()),
                    str(summary.week_end.date()),
                    datetime.now(timezone.utc).isoformat(),
                ],
            }
        )
        metadata.to_excel(writer, sheet_name="metadata", index=False)
        summary.ranking.to_excel(writer, sheet_name="ranking", index=False)
        summary.trending.to_excel(writer, sheet_name="trending", index=False)
    return output.getvalue()


def export_drilldown_csv(drilldown: pd.DataFrame) -> bytes:
    """Export drill-down records with shipping details to CSV.

    Complexity:
    - Time: O(k), where k is number of drill-down rows.
    - Space: O(k) for serialized buffer.
    """

    return drilldown.to_csv(index=False).encode("utf-8")
