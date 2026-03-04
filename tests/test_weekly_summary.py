"""Unit test stubs for weekly summary generation.

These tests describe expected outputs such as sorted ranking by issue count
and the presence of an `issue_rule` description for UI display (AC-6, AC-8).
"""

from datetime import date

import pytest

from src.reports.weekly_summary import WeeklySummaryGenerator


def test_weekly_summary_generate_stub():
    gen = WeeklySummaryGenerator()
    with pytest.raises(NotImplementedError):
        gen.generate([], week_start=date(2025, 1, 6), week_end=date(2025, 1, 12))
