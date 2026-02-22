"""Unit test stubs for trending calculations.

Tests will later ensure categories are grouped and deltas computed (AC-10, AC-11).
"""
import pytest
from datetime import date

from src.reports.trending import TrendingCalculator


def test_trending_compute_stub():
    t = TrendingCalculator()
    with pytest.raises(NotImplementedError):
        t.compute([], week_start=date(2025, 1, 6), week_end=date(2025, 1, 12), prev_start=date(2024, 12, 30), prev_end=date(2025, 1, 5))
