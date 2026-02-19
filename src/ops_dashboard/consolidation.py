"""Consolidation pipeline that merges production and shipping logs.

This module implements AC-1 through AC-5 and portions of AC-13/16/17 by
normalizing IDs, parsing dates, joining datasets, and flagging data quality
issues with traceability metadata.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import pandas as pd

from ops_dashboard.models import ConsolidationResult
from ops_dashboard.normalization import normalize_lot_id, parse_mixed_date, truthy_issue_flag


def _coalesce_column(df: pd.DataFrame, candidates: list[str], default: Any = None) -> pd.Series:
    """Return first existing candidate column from DataFrame.

    Complexity:
    - Time: O(candidates) lookup + O(r) for returning series.
    - Space: O(1) additional storage.
    """

    for name in candidates:
        if name in df.columns:
            return df[name]
    return pd.Series([default] * len(df), index=df.index)


def _prepare_production(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize production schema, dates, issue flags, and lot IDs.

    Complexity:
    - Time: O(r), where r is number of production rows.
    - Space: O(r) for new derived columns.
    """

    out = df.copy()
    out["raw_lot_id"] = _coalesce_column(out, ["raw_lot_id", "lot_id", "lot", "lot_number"])
    out["production_line"] = _coalesce_column(out, ["production_line", "line_name", "line"])
    out["primary_issue"] = _coalesce_column(out, ["primary_issue", "issue_category", "defect_category"])
    out["line_issue"] = _coalesce_column(out, ["line_issue", "line_issue_flag", "issue"]).map(truthy_issue_flag)
    out["production_date_raw"] = _coalesce_column(out, ["production_date", "run_date", "date"])
    out["provided_normalized_lot_id"] = _coalesce_column(out, ["normalized_lot_id"], default=None)

    parsed_dates: list[pd.Timestamp | pd.NaT] = []
    date_errors: list[str | None] = []
    canonical_ids: list[str | None] = []
    lot_status: list[str] = []
    lot_reasons: list[str | None] = []

    for value in out["production_date_raw"]:
        parsed, reason = parse_mixed_date(value)
        parsed_dates.append(parsed)
        date_errors.append(reason)

    for value in out["raw_lot_id"]:
        normalized = normalize_lot_id(value)
        canonical_ids.append(normalized.canonical_lot_id)
        lot_status.append(normalized.status)
        lot_reasons.append(normalized.reason)

    out["production_date"] = parsed_dates
    out["date_error_reason"] = date_errors
    out["canonical_lot_id"] = canonical_ids
    out["lot_normalization_status"] = lot_status
    out["lot_error_reason"] = lot_reasons
    out["needs_review"] = out["date_error_reason"].notna() | (out["lot_normalization_status"] != "ok")
    out["review_reason"] = out["date_error_reason"].fillna("") + out["lot_error_reason"].fillna("")
    # Ambiguous mapping: a provided normalized value disagrees with computed canonical lot.
    provided = out["provided_normalized_lot_id"].map(lambda x: normalize_lot_id(x).canonical_lot_id if pd.notna(x) else None)
    mismatch = provided.notna() & out["canonical_lot_id"].notna() & provided.ne(out["canonical_lot_id"])
    out.loc[mismatch, "needs_review"] = True
    out.loc[mismatch, "review_reason"] = "Ambiguous lot match: provided normalized_lot_id conflicts with raw lot normalization"
    out["dataset"] = "production"
    return out


def _prepare_shipping(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize shipping schema, dates, statuses, and lot IDs.

    Complexity:
    - Time: O(r), where r is number of shipping rows.
    - Space: O(r) for derived columns.
    """

    out = df.copy()
    out["raw_lot_id"] = _coalesce_column(out, ["raw_lot_id", "lot_id", "lot", "lot_number"])
    out["ship_status"] = _coalesce_column(out, ["ship_status", "shipping_status"]).fillna("On Hold")
    out["ship_date_raw"] = _coalesce_column(out, ["ship_date", "shipping_date", "date"])
    out["provided_normalized_lot_id"] = _coalesce_column(out, ["normalized_lot_id"], default=None)

    parsed_dates: list[pd.Timestamp | pd.NaT] = []
    date_errors: list[str | None] = []
    canonical_ids: list[str | None] = []
    lot_status: list[str] = []
    lot_reasons: list[str | None] = []

    for value in out["ship_date_raw"]:
        parsed, reason = parse_mixed_date(value)
        parsed_dates.append(parsed)
        date_errors.append(reason)

    for value in out["raw_lot_id"]:
        normalized = normalize_lot_id(value)
        canonical_ids.append(normalized.canonical_lot_id)
        lot_status.append(normalized.status)
        lot_reasons.append(normalized.reason)

    out["ship_date"] = parsed_dates
    out["date_error_reason"] = date_errors
    out["canonical_lot_id"] = canonical_ids
    out["lot_normalization_status"] = lot_status
    out["lot_error_reason"] = lot_reasons
    out["needs_review"] = out["date_error_reason"].notna() | (out["lot_normalization_status"] != "ok")
    out["review_reason"] = out["date_error_reason"].fillna("") + out["lot_error_reason"].fillna("")
    provided = out["provided_normalized_lot_id"].map(lambda x: normalize_lot_id(x).canonical_lot_id if pd.notna(x) else None)
    mismatch = provided.notna() & out["canonical_lot_id"].notna() & provided.ne(out["canonical_lot_id"])
    out.loc[mismatch, "needs_review"] = True
    out.loc[mismatch, "review_reason"] = "Ambiguous lot match: provided normalized_lot_id conflicts with raw lot normalization"
    out["dataset"] = "shipping"
    return out


def _latest_shipping_by_lot(shipping: pd.DataFrame) -> pd.DataFrame:
    """Select the latest shipping row per canonical lot.

    Complexity:
    - Time: O(r log r) due to sorting by ship date.
    - Space: O(r) for sorted frame copy.
    """

    valid = shipping[shipping["canonical_lot_id"].notna()].copy()
    valid = valid.sort_values(["canonical_lot_id", "ship_date"], ascending=[True, False])
    latest = valid.drop_duplicates(subset=["canonical_lot_id"], keep="first")
    return latest


def _detect_conflicts(production: pd.DataFrame, shipping: pd.DataFrame) -> pd.DataFrame:
    """Find conflicting key values for same canonical lot across source rows.

    A conflict is present when a lot maps to multiple production lines or
    multiple shipping statuses.

    Complexity:
    - Time: O(p + s), where p and s are row counts in each input.
    - Space: O(u), where u is number of unique canonical lots.
    """

    records: list[dict[str, Any]] = []
    by_lot_production = production[production["canonical_lot_id"].notna()].groupby("canonical_lot_id")
    by_lot_shipping = shipping[shipping["canonical_lot_id"].notna()].groupby("canonical_lot_id")
    lot_ids = sorted(set(by_lot_production.groups.keys()) | set(by_lot_shipping.groups.keys()))

    for lot_id in lot_ids:
        prod_rows = by_lot_production.get_group(lot_id) if lot_id in by_lot_production.groups else pd.DataFrame()
        ship_rows = by_lot_shipping.get_group(lot_id) if lot_id in by_lot_shipping.groups else pd.DataFrame()
        prod_lines = {v for v in prod_rows.get("production_line", pd.Series(dtype="object")).dropna().unique()}
        ship_statuses = {v for v in ship_rows.get("ship_status", pd.Series(dtype="object")).dropna().unique()}
        if len(prod_lines) > 1 or len(ship_statuses) > 1:
            # Keep compact competing row references for UI drill-through.
            records.append(
                {
                    "canonical_lot_id": lot_id,
                    "conflict_production_lines": sorted(prod_lines),
                    "conflict_ship_statuses": sorted(ship_statuses),
                    "production_sources": prod_rows[["source_file", "source_sheet", "source_row"]]
                    .drop_duplicates()
                    .to_dict("records"),
                    "shipping_sources": ship_rows[["source_file", "source_sheet", "source_row"]]
                    .drop_duplicates()
                    .to_dict("records"),
                }
            )
    return pd.DataFrame(records)


def consolidate_logs(
    production_df: pd.DataFrame,
    shipping_df: pd.DataFrame,
    include_flagged: bool = False,
) -> ConsolidationResult:
    """Consolidate production and shipping logs into reporting-ready tables.

    The function enforces canonical lot matching and records rows that require
    manual review.

    Complexity:
    - Time: O(p log p + s log s) dominated by latest-shipping sort operations.
    - Space: O(p + s) for transformed DataFrames.
    """

    production = _prepare_production(production_df)
    shipping = _prepare_shipping(shipping_df)
    shipping_latest = _latest_shipping_by_lot(shipping)

    consolidated = production.merge(
        shipping_latest[
            [
                "canonical_lot_id",
                "ship_status",
                "ship_date",
                "source_file",
                "source_sheet",
                "source_row",
                "raw_lot_id",
            ]
        ].rename(
            columns={
                "source_file": "shipping_source_file",
                "source_sheet": "shipping_source_sheet",
                "source_row": "shipping_source_row",
                "raw_lot_id": "shipping_raw_lot_id",
            }
        ),
        on="canonical_lot_id",
        how="left",
    )

    # Missing shipping matches are review-worthy for cross-file reconciliation.
    consolidated["shipping_match_status"] = consolidated["ship_status"].notna().map(lambda ok: "matched" if ok else "unmatched")
    consolidated["needs_review"] = consolidated["needs_review"] | (consolidated["shipping_match_status"] == "unmatched")
    consolidated["review_reason"] = consolidated["review_reason"].where(
        consolidated["review_reason"].astype(str).str.len() > 0,
        "No matching shipping lot found",
    )
    consolidated["is_problematic_but_shipped"] = consolidated["line_issue"] & consolidated["ship_status"].isin(["Shipped", "Partial"])

    conflict_rows = _detect_conflicts(production, shipping)
    if not conflict_rows.empty:
        conflict_lots = set(conflict_rows["canonical_lot_id"])
        consolidated["has_conflict"] = consolidated["canonical_lot_id"].isin(conflict_lots)
    else:
        consolidated["has_conflict"] = False

    flagged_rows = consolidated[consolidated["needs_review"]].copy()
    if not include_flagged:
        consolidated = consolidated[~consolidated["needs_review"]].copy()

    # Build alias evidence map for traceability and conflict investigations.
    alias_lookup: dict[str, set[str]] = defaultdict(set)
    for frame in (production, shipping):
        for _, row in frame[frame["canonical_lot_id"].notna()][["canonical_lot_id", "raw_lot_id"]].iterrows():
            alias_lookup[row["canonical_lot_id"]].add(str(row["raw_lot_id"]))
    consolidated["raw_lot_aliases"] = consolidated["canonical_lot_id"].map(lambda lot: sorted(alias_lookup.get(lot, set())))

    return ConsolidationResult(
        production=production,
        shipping=shipping,
        consolidated=consolidated,
        flagged_rows=flagged_rows,
        conflict_rows=conflict_rows,
    )
