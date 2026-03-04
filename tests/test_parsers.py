"""Unit test stubs for parser utilities.

Each test is a placeholder demonstrating the intent: concrete implementations
should test parsing of multiple date formats, missing/invalid values, and
that `SpreadsheetLoader` yields `SourceReference` metadata for rows.
"""

import pytest

from src import parsers


def test_parse_date_accepts_common_formats():
    """Verify `parse_date` accepts several common formats and returns datetime.

    This test validates the minimal parsing capabilities required by AC-2.
    """
    from datetime import datetime

    dt1 = parsers.parse_date("2025-01-01")
    assert (
        isinstance(dt1, datetime)
        and dt1.year == 2025
        and dt1.month == 1
        and dt1.day == 1
    )

    dt2 = parsers.parse_date("01/02/2025")
    assert (
        isinstance(dt2, datetime)
        and dt2.year == 2025
        and dt2.month == 1
        and dt2.day == 2
    )

    dt3 = parsers.parse_date("Jan 2, 2025")
    assert (
        isinstance(dt3, datetime)
        and dt3.year == 2025
        and dt3.month == 1
        and dt3.day == 2
    )


def test_spreadsheet_loader_yields_rows_and_source_reference():
    """TODO: implement loader and assert it yields (row_dict, SourceReference).

    This test currently asserts the API shape via NotImplementedError.
    """

    loader = parsers.SpreadsheetLoader()
    with pytest.raises(NotImplementedError):
        list(loader.load_files(["dummy_path.xlsx"]))
