"""Streamlit UI for weekly production issue summary and drill-down workflows."""

from __future__ import annotations

import io
from datetime import date

import pandas as pd
import streamlit as st

from ops_dashboard.config import AppConfig
from ops_dashboard.consolidation import consolidate_logs
from ops_dashboard.exporting import export_drilldown_csv, export_weekly_summary_csv, export_weekly_summary_xlsx
from ops_dashboard.reporting import ReportingService


def _read_upload(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> pd.DataFrame:
    """Read uploaded CSV/XLSX content into a DataFrame.

    Complexity:
    - Time: O(r * c), proportional to uploaded sheet size.
    - Space: O(r * c) for in-memory DataFrame.
    """

    file_name = uploaded_file.name.lower()
    raw_bytes = uploaded_file.getvalue()
    if file_name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(raw_bytes))
    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(raw_bytes))
    else:
        raise ValueError("Only CSV and Excel uploads are supported.")
    # Add source traceability metadata for AC-17.
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("/", "_") for c in df.columns]
    df["source_file"] = uploaded_file.name
    df["source_sheet"] = "Sheet1"
    df["source_row"] = (df.index + 2).astype(int)
    return df


def main() -> None:
    """Render and run the Streamlit application.

    Complexity:
    - Time/Space: Driven by user-triggered DataFrame operations in callbacks.
    """

    st.set_page_config(page_title="Ops Weekly Summary", layout="wide")
    st.title("Operations Weekly Summary")
    st.caption("Consolidate Production + Shipping logs, then answer weekly reporting questions quickly.")

    with st.sidebar:
        st.header("Configuration")
        issue_rule_text = st.text_area(
            "Issue Rule (shown in UI)",
            value="Count row as issue when line_issue is truthy (Yes/True/1).",
            help="AC-6: This text explains exactly how issue_count is computed.",
        )
        not_found_label = st.text_input(
            "Missing Shipping Label",
            value="Not Found / Not Shipped Yet",
            help="AC-14: Label shown when a production lot has no matching shipping record.",
        )
        include_flagged = st.checkbox(
            "Include Needs Review rows in summaries",
            value=False,
            help="AC-5: Flagged rows are excluded by default unless explicitly included.",
        )

    # AC-1: user selects both Production and Shipping files for consolidation.
    production_file = st.file_uploader("Upload Production Log (CSV/XLSX)", type=["csv", "xlsx", "xls"], key="prod")
    shipping_file = st.file_uploader("Upload Shipping Log (CSV/XLSX)", type=["csv", "xlsx", "xls"], key="ship")

    if production_file is None or shipping_file is None:
        st.info("Upload both files to generate weekly summary reports.")
        return

    production_df = _read_upload(production_file)
    shipping_df = _read_upload(shipping_file)
    config = AppConfig(issue_rule_text=issue_rule_text, not_found_shipping_label=not_found_label)
    consolidation = consolidate_logs(production_df, shipping_df, include_flagged=include_flagged)
    service = ReportingService(config=config)

    st.subheader("Consolidation Status")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Production rows", len(consolidation.production))
    col_b.metric("Shipping rows", len(consolidation.shipping))
    col_c.metric("Needs Review rows", len(consolidation.flagged_rows))

    with st.expander("Issue counting rule", expanded=False):
        st.write(config.issue_rule_text)

    if not consolidation.flagged_rows.empty:
        st.warning("Some rows are flagged as Needs Review and may be excluded from summaries.")
        st.dataframe(
            consolidation.flagged_rows[
                [
                    "dataset",
                    "source_file",
                    "source_sheet",
                    "source_row",
                    "raw_lot_id",
                    "canonical_lot_id",
                    "review_reason",
                ]
            ],
            use_container_width=True,
        )

    selected_date = st.date_input("Select week anchor date", value=date.today())
    summary = service.weekly_summary(consolidation.consolidated, pd.Timestamp(selected_date))

    st.subheader(f"Weekly Summary ({summary.week_start.date()} to {summary.week_end.date()})")
    st.markdown("### Production Line Ranking")
    st.dataframe(summary.ranking, use_container_width=True)

    st.markdown("### Trending Issue Categories")
    st.dataframe(summary.trending, use_container_width=True)

    csv_summary = export_weekly_summary_csv(summary)
    xlsx_summary = export_weekly_summary_xlsx(summary)
    st.download_button(
        "Export Weekly Summary (CSV)",
        data=csv_summary,
        file_name=f"weekly_summary_{summary.week_start.date()}_{summary.week_end.date()}.csv",
        mime="text/csv",
    )
    st.download_button(
        "Export Weekly Summary (XLSX)",
        data=xlsx_summary,
        file_name=f"weekly_summary_{summary.week_start.date()}_{summary.week_end.date()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown("## Drill-down")
    line_options = summary.ranking["production_line"].dropna().tolist()
    selected_line = st.selectbox("Select production line", options=line_options if line_options else ["(none)"])
    if line_options:
        line_drill = service.drill_down_by_line(consolidation.consolidated, selected_line, pd.Timestamp(selected_date))
        st.markdown("### Line Drill-down (Issue rows)")
        st.dataframe(line_drill, use_container_width=True)
        st.download_button(
            "Export Line Drill-down (CSV)",
            data=export_drilldown_csv(line_drill),
            file_name=f"line_drilldown_{selected_line}_{summary.week_start.date()}.csv",
            mime="text/csv",
        )

    category_options = summary.trending["issue_category"].tolist() if not summary.trending.empty else []
    selected_category = st.selectbox(
        "Select issue category",
        options=category_options if category_options else ["(none)"],
    )
    include_prev = st.checkbox("Include previous week in category drill-down", value=False)
    if category_options:
        category_drill = service.drill_down_by_category(
            consolidation.consolidated,
            selected_category,
            pd.Timestamp(selected_date),
            include_previous_period=include_prev,
        )
        st.markdown("### Category Drill-down")
        st.dataframe(category_drill, use_container_width=True)
        st.download_button(
            "Export Category Drill-down (CSV)",
            data=export_drilldown_csv(category_drill),
            file_name=f"category_drilldown_{selected_category}_{summary.week_start.date()}.csv",
            mime="text/csv",
        )

    if not consolidation.conflict_rows.empty:
        st.markdown("## Conflict Detection")
        st.error("Conflicting key values detected for one or more canonical lots.")
        st.dataframe(consolidation.conflict_rows, use_container_width=True)


if __name__ == "__main__":
    main()
