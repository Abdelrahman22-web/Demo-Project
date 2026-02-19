"""Reporting service for weekly rankings, trends, and drill-down views."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ops_dashboard.config import AppConfig
from ops_dashboard.models import WeeklySummaryResult


def week_bounds(anchor_date: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return Monday-Sunday bounds for the given date.

    Complexity:
    - Time: O(1).
    - Space: O(1).
    """

    normalized = pd.Timestamp(anchor_date).normalize()
    start = normalized - pd.Timedelta(days=normalized.weekday())
    end = start + pd.Timedelta(days=6)
    return start, end


@dataclass(slots=True)
class ReportingService:
    """Business service for generating summaries from consolidated rows.

    Complexity:
    - Time: O(1) for construction.
    - Space: O(1).
    """

    config: AppConfig

    def weekly_summary(self, consolidated: pd.DataFrame, anchor_date: pd.Timestamp) -> WeeklySummaryResult:
        """Generate weekly line ranking and category trend vs previous week.

        Complexity:
        - Time: O(r + g log g), where r is row count and g group count.
        - Space: O(r + g) for filtered and grouped intermediates.
        """

        week_start, week_end = week_bounds(anchor_date)
        prev_start = week_start - pd.Timedelta(days=self.config.comparison_period_days)
        prev_end = week_end - pd.Timedelta(days=self.config.comparison_period_days)

        current = consolidated[
            (consolidated["production_date"] >= week_start) & (consolidated["production_date"] <= week_end)
        ].copy()
        previous = consolidated[
            (consolidated["production_date"] >= prev_start) & (consolidated["production_date"] <= prev_end)
        ].copy()

        ranking = (
            current.groupby("production_line", dropna=False)
            .agg(
                issue_count=("line_issue", "sum"),
                total_rows=("line_issue", "size"),
                unique_lots=("canonical_lot_id", "nunique"),
            )
            .reset_index()
            .sort_values(["issue_count", "total_rows", "production_line"], ascending=[False, False, True])
        )

        cur_trend = (
            current[current["line_issue"]]
            .assign(issue_category=lambda df: df["primary_issue"].fillna("Unspecified"))
            .groupby("issue_category")
            .size()
            .rename("current_count")
        )
        prev_trend = (
            previous[previous["line_issue"]]
            .assign(issue_category=lambda df: df["primary_issue"].fillna("Unspecified"))
            .groupby("issue_category")
            .size()
            .rename("previous_count")
        )
        trending = pd.concat([cur_trend, prev_trend], axis=1).fillna(0).astype(int).reset_index()
        trending["delta"] = trending["current_count"] - trending["previous_count"]
        trending["direction"] = trending["delta"].map(lambda d: "up" if d > 0 else ("down" if d < 0 else "flat"))
        trending = trending.sort_values(["current_count", "delta", "issue_category"], ascending=[False, False, True])

        return WeeklySummaryResult(week_start=week_start, week_end=week_end, ranking=ranking, trending=trending)

    def drill_down_by_line(self, consolidated: pd.DataFrame, line_name: str, anchor_date: pd.Timestamp) -> pd.DataFrame:
        """Return issue-contributing rows for a selected production line.

        Complexity:
        - Time: O(r), where r is row count (boolean filtering).
        - Space: O(k) for result rows.
        """

        week_start, week_end = week_bounds(anchor_date)
        rows = consolidated[
            (consolidated["production_line"] == line_name)
            & (consolidated["production_date"] >= week_start)
            & (consolidated["production_date"] <= week_end)
            & (consolidated["line_issue"])
        ].copy()
        rows["shipping_status_display"] = rows["ship_status"].fillna(self.config.not_found_shipping_label)
        rows["latest_ship_date_display"] = rows["ship_date"]
        return rows.sort_values(["production_date", "canonical_lot_id"], ascending=[False, True])

    def drill_down_by_category(
        self,
        consolidated: pd.DataFrame,
        category: str,
        anchor_date: pd.Timestamp,
        include_previous_period: bool = False,
    ) -> pd.DataFrame:
        """Return affected lots for a selected issue category.

        Complexity:
        - Time: O(r), where r is row count.
        - Space: O(k) for filtered rows.
        """

        week_start, week_end = week_bounds(anchor_date)
        frame = consolidated
        if include_previous_period:
            prev_start = week_start - pd.Timedelta(days=self.config.comparison_period_days)
            # Include both current and previous windows for side-by-side analysis.
            frame = frame[
                (frame["production_date"] >= prev_start)
                & (frame["production_date"] <= week_end)
            ]
        else:
            frame = frame[
                (frame["production_date"] >= week_start)
                & (frame["production_date"] <= week_end)
            ]

        rows = frame[
            frame["line_issue"]
            & frame["primary_issue"].fillna("Unspecified").eq(category)
        ].copy()
        rows["shipping_status_display"] = rows["ship_status"].fillna(self.config.not_found_shipping_label)
        rows["is_problematic_but_shipped"] = rows["shipping_status_display"].isin(["Shipped", "Partial"])
        return rows.sort_values(["production_date", "canonical_lot_id"], ascending=[False, True])
