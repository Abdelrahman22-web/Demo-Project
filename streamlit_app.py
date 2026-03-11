from __future__ import annotations

import tempfile
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.config import load_settings
from src.consolidation import Consolidator
from src.exporter import Exporter
from src.normalization import LotNormalizer
from src.parsers import SpreadsheetLoader
from src.reports.trending import TrendingCalculator
from src.reports.weekly_summary import WeeklySummaryGenerator

st.set_page_config(page_title="Ops Weekly Summary", layout="wide")


def _save_upload(upload) -> str:
    suffix = Path(upload.name).suffix or ".csv"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(upload.getvalue())
        return handle.name


def _to_frame(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def main() -> None:
    settings = load_settings()
    st.title("Ops Weekly Summary")
    st.caption(
        f"Environment: {settings.app_env} | Test DB: {settings.test_database_url}"
    )

    with st.sidebar:
        st.header("Inputs")
        production_file = st.file_uploader("Production CSV", type=["csv"])
        shipping_file = st.file_uploader("Shipping CSV", type=["csv"])
        include_flagged = st.checkbox("Include Needs Review rows", value=False)
        anchor_date = st.date_input("Week anchor date", value=date(2026, 1, 18))

    if not production_file or not shipping_file:
        st.info("Upload both CSV files to generate the dashboard.")
        return

    week_start = anchor_date - timedelta(days=anchor_date.weekday())
    week_end = week_start + timedelta(days=6)
    prev_start = week_start - timedelta(days=7)
    prev_end = week_start - timedelta(days=1)

    production_path = _save_upload(production_file)
    shipping_path = _save_upload(shipping_file)

    consolidator = Consolidator(SpreadsheetLoader(), LotNormalizer())
    result = consolidator.consolidate(
        [production_path, shipping_path], include_flagged=include_flagged
    )

    summary = WeeklySummaryGenerator().generate(result.rows, week_start, week_end)
    trending = TrendingCalculator().compute(
        result.rows, week_start, week_end, prev_start, prev_end
    )

    st.subheader("Weekly Line Ranking")
    st.dataframe(_to_frame(summary["ranking"]), use_container_width=True)

    st.subheader("Trending Issue Categories")
    st.dataframe(_to_frame(trending["categories"]), use_container_width=True)

    st.subheader("Consolidated Production Records")
    st.dataframe(_to_frame(result.rows), use_container_width=True)

    if result.needs_review:
        st.subheader("Needs Review")
        st.dataframe(_to_frame(result.needs_review), use_container_width=True)

    exporter = Exporter(output_dir=Path(tempfile.gettempdir()))
    ranking_csv = exporter.export_csv(summary["ranking"], "weekly_summary.csv")
    summary_xlsx = exporter.export_xlsx(
        {"ranking": summary["ranking"], "trending": trending["categories"]},
        "weekly_summary.xlsx",
    )

    st.download_button(
        "Download Weekly Summary CSV",
        data=ranking_csv.read_bytes(),
        file_name=ranking_csv.name,
        mime="text/csv",
    )
    st.download_button(
        "Download Weekly Summary XLSX",
        data=BytesIO(summary_xlsx.read_bytes()),
        file_name=summary_xlsx.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    main()
