"""Shared pytest fixtures for ops weekly summary tests."""

import pandas as pd
import pytest


@pytest.fixture()
def production_df() -> pd.DataFrame:
    """Return representative production rows with mixed formats and issues.

    Complexity:
    - Time: O(1) fixture creation with fixed-size in-memory data.
    - Space: O(1) for fixed row count in tests.
    """

    return pd.DataFrame(
        [
            {
                "production_date": "2026-02-02",
                "production_line": "Line 1",
                "raw_lot_id": " LOT_20260202-001 ",
                "line_issue": "Yes",
                "primary_issue": "Tool wear",
                "source_file": "prod.xlsx",
                "source_sheet": "Production",
                "source_row": 2,
            },
            {
                "production_date": "02/03/2026",
                "production_line": "Line 2",
                "raw_lot_id": "L0T-20260203-001",
                "line_issue": "No",
                "primary_issue": None,
                "source_file": "prod.xlsx",
                "source_sheet": "Production",
                "source_row": 3,
            },
            {
                "production_date": "2026/02/04",
                "production_line": "Line 1",
                "raw_lot_id": "LOT20260204001",
                "line_issue": "1",
                "primary_issue": "Sensor fault",
                "source_file": "prod.xlsx",
                "source_sheet": "Production",
                "source_row": 4,
            },
            {
                "production_date": "bad-date",
                "production_line": "Line 3",
                "raw_lot_id": "BADLOT",
                "line_issue": "Yes",
                "primary_issue": "Material shortage",
                "source_file": "prod.xlsx",
                "source_sheet": "Production",
                "source_row": 5,
            },
        ]
    )


@pytest.fixture()
def shipping_df() -> pd.DataFrame:
    """Return representative shipping rows with matching, missing, and conflict data.

    Complexity:
    - Time: O(1).
    - Space: O(1).
    """

    return pd.DataFrame(
        [
            {
                "ship_date": "2026-02-05",
                "raw_lot_id": "LOT-20260202-001",
                "ship_status": "Shipped",
                "source_file": "ship.xlsx",
                "source_sheet": "Shipping",
                "source_row": 2,
            },
            {
                "ship_date": "2026-02-06",
                "raw_lot_id": "LOT-20260203-001",
                "ship_status": "On Hold",
                "source_file": "ship.xlsx",
                "source_sheet": "Shipping",
                "source_row": 3,
            },
            {
                "ship_date": "2026-02-07",
                "raw_lot_id": "LOT-20260203-001",
                "ship_status": "Partial",
                "source_file": "ship.xlsx",
                "source_sheet": "Shipping",
                "source_row": 4,
            },
            {
                "ship_date": "not-a-date",
                "raw_lot_id": "LOT-20260208-001",
                "ship_status": "Shipped",
                "source_file": "ship.xlsx",
                "source_sheet": "Shipping",
                "source_row": 5,
            },
        ]
    )
