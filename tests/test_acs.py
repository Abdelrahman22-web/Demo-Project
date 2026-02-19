"""Acceptance-criteria-focused tests for AC-1 through AC-19 coverage."""

from __future__ import annotations

import pandas as pd

from ops_dashboard.config import AppConfig
from ops_dashboard.consolidation import consolidate_logs
from ops_dashboard.exporting import export_drilldown_csv, export_weekly_summary_csv, export_weekly_summary_xlsx
from ops_dashboard.reporting import ReportingService


def _service() -> ReportingService:
    """Return a reporting service with deterministic test config."""

    return ReportingService(AppConfig(issue_rule_text="Test rule", not_found_shipping_label="Not Shipped Yet"))


def test_ac1_ac4_consolidates_and_matches_lots(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-1/AC-4: loads two datasets and matches by canonical lot ID."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=True)
    assert not result.consolidated.empty
    # L0T typo and separator differences should resolve to same canonical lot.
    line2 = result.consolidated[result.consolidated["production_line"] == "Line 2"].iloc[0]
    assert line2["canonical_lot_id"] == "LOT-20260203-001"
    assert line2["ship_status"] in {"On Hold", "Partial"}


def test_ac2_standardizes_dates_and_flags_unparseable(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-2: parse mixed formats and flag invalid date rows with reason."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=True)
    bad_prod = result.production[result.production["source_row"] == 5].iloc[0]
    bad_ship = result.shipping[result.shipping["source_row"] == 5].iloc[0]
    assert pd.isna(bad_prod["production_date"])
    assert "Unparseable date value" in bad_prod["date_error_reason"]
    assert pd.isna(bad_ship["ship_date"])
    assert "Unparseable date value" in bad_ship["date_error_reason"]


def test_ac3_keeps_raw_lot_and_generates_canonical(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-3: raw lot ID is preserved and canonical lot is generated."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=True)
    row = result.production[result.production["source_row"] == 2].iloc[0]
    assert row["raw_lot_id"].strip() == "LOT_20260202-001"
    assert row["canonical_lot_id"] == "LOT-20260202-001"


def test_ac5_flags_and_excludes_needs_review_by_default(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-5: review rows are flagged and excluded unless include_flagged is True."""

    excluded = consolidate_logs(production_df, shipping_df, include_flagged=False)
    included = consolidate_logs(production_df, shipping_df, include_flagged=True)
    assert len(included.flagged_rows) >= 1
    assert len(excluded.consolidated) < len(included.consolidated)


def test_ac6_to_ac9_weekly_ranking_and_line_drilldown(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-6/7/8/9: issue rule usage, week filter, ranking order, and drill-down rows."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=False)
    service = _service()
    summary = service.weekly_summary(result.consolidated, pd.Timestamp("2026-02-04"))
    assert summary.week_start == pd.Timestamp("2026-02-02")
    assert summary.week_end == pd.Timestamp("2026-02-08")
    assert summary.ranking.iloc[0]["issue_count"] >= summary.ranking.iloc[-1]["issue_count"]
    drill = service.drill_down_by_line(result.consolidated, "Line 1", pd.Timestamp("2026-02-04"))
    assert not drill.empty
    assert drill["line_issue"].all()


def test_ac10_to_ac12_trending_and_category_drilldown(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-10/11/12: category grouping, deltas vs previous week, and category drill-down."""

    previous_week_row = pd.DataFrame(
        [
            {
                "production_date": "2026-01-27",
                "production_line": "Line 1",
                "raw_lot_id": "LOT-20260127-001",
                "line_issue": "Yes",
                "primary_issue": "Tool wear",
                "source_file": "prod.xlsx",
                "source_sheet": "Production",
                "source_row": 6,
            }
        ]
    )
    production = pd.concat([production_df, previous_week_row], ignore_index=True)
    result = consolidate_logs(production, shipping_df, include_flagged=False)
    service = _service()
    summary = service.weekly_summary(result.consolidated, pd.Timestamp("2026-02-04"))
    assert {"issue_category", "current_count", "previous_count", "delta", "direction"}.issubset(summary.trending.columns)
    category = summary.trending.iloc[0]["issue_category"]
    drill = service.drill_down_by_category(result.consolidated, category, pd.Timestamp("2026-02-04"), include_previous_period=True)
    assert not drill.empty


def test_ac13_to_ac15_shipping_status_and_problematic_shipped_flag(
    production_df: pd.DataFrame, shipping_df: pd.DataFrame
) -> None:
    """AC-13/14/15: shipping state shown, missing shipping labeled, shipped problems highlighted."""

    extra_prod = pd.DataFrame(
        [
            {
                "production_date": "2026-02-05",
                "production_line": "Line 4",
                "raw_lot_id": "LOT-20260205-001",
                "line_issue": "Yes",
                "primary_issue": "Tool wear",
                "source_file": "prod.xlsx",
                "source_sheet": "Production",
                "source_row": 7,
            }
        ]
    )
    production = pd.concat([production_df, extra_prod], ignore_index=True)
    result = consolidate_logs(production, shipping_df, include_flagged=True)
    service = _service()
    drill = service.drill_down_by_line(result.consolidated, "Line 1", pd.Timestamp("2026-02-04"))
    assert "shipping_status_display" in drill.columns
    assert drill["shipping_status_display"].isin(["Shipped", "Partial", "On Hold", "Not Shipped Yet"]).all()
    shipped_problem = result.consolidated[result.consolidated["canonical_lot_id"] == "LOT-20260202-001"].iloc[0]
    assert bool(shipped_problem["is_problematic_but_shipped"]) is True


def test_ac16_conflict_detection_includes_competing_sources(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-16: conflicting key values are flagged with competing source rows."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=True)
    conflicts = result.conflict_rows
    assert not conflicts.empty
    row = conflicts[conflicts["canonical_lot_id"] == "LOT-20260203-001"].iloc[0]
    assert "On Hold" in row["conflict_ship_statuses"]
    assert "Partial" in row["conflict_ship_statuses"]
    assert len(row["shipping_sources"]) >= 2


def test_ac17_traceability_fields_present(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-17: consolidated rows include source file/sheet/row and raw values."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=True)
    row = result.consolidated.iloc[0]
    assert {"source_file", "source_sheet", "source_row", "raw_lot_id"}.issubset(result.consolidated.columns)
    assert row["source_file"] == "prod.xlsx"


def test_ac18_weekly_export_contains_tables_and_metadata(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-18: weekly summary export includes ranking, trending, week range, timestamp."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=False)
    summary = _service().weekly_summary(result.consolidated, pd.Timestamp("2026-02-04"))
    csv_bytes = export_weekly_summary_csv(summary)
    csv_text = csv_bytes.decode("utf-8")
    assert "week_start,2026-02-02" in csv_text
    assert "ranking_table" in csv_text
    assert "trending_table" in csv_text
    xlsx_bytes = export_weekly_summary_xlsx(summary)
    assert len(xlsx_bytes) > 0


def test_ac19_drilldown_export_contains_shipping_fields(production_df: pd.DataFrame, shipping_df: pd.DataFrame) -> None:
    """AC-19: drill-down export contains issue and shipping status fields."""

    result = consolidate_logs(production_df, shipping_df, include_flagged=False)
    drill = _service().drill_down_by_line(result.consolidated, "Line 1", pd.Timestamp("2026-02-04"))
    payload = export_drilldown_csv(drill).decode("utf-8")
    assert "canonical_lot_id" in payload
    assert "primary_issue" in payload
    assert "shipping_status_display" in payload
