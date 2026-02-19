"""Typed data containers for consolidated and reporting datasets.

These structures provide self-describing return values between modules.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass(slots=True)
class ConsolidationResult:
    """Output object for the spreadsheet consolidation step.

    Attributes:
    - production: Normalized production rows with quality flags.
    - shipping: Normalized shipping rows with quality flags.
    - consolidated: Joined production + shipping view for reports.
    - flagged_rows: Subset needing review due to quality/matching issues.
    - conflict_rows: Potential data conflicts for same canonical lot id.

    Complexity:
    - Time: O(1) object creation; references pre-built DataFrames.
    - Space: O(1) additional storage beyond references.
    """

    production: pd.DataFrame
    shipping: pd.DataFrame
    consolidated: pd.DataFrame
    flagged_rows: pd.DataFrame
    conflict_rows: pd.DataFrame


@dataclass(slots=True)
class WeeklySummaryResult:
    """Aggregated weekly results used by both UI and export layers.

    Attributes:
    - week_start: Inclusive Monday for selected week.
    - week_end: Inclusive Sunday for selected week.
    - ranking: Production lines sorted by issue count descending.
    - trending: Issue/defect category trend with deltas vs previous week.

    Complexity:
    - Time: O(1) object creation.
    - Space: O(1) additional storage.
    """

    week_start: pd.Timestamp
    week_end: pd.Timestamp
    ranking: pd.DataFrame
    trending: pd.DataFrame
