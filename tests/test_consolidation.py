"""Unit test stubs for consolidation logic.

These tests outline expected inputs/outputs for the `Consolidator`.
"""
import pytest

from src.consolidation import Consolidator
from src.parsers import SpreadsheetLoader
from src.normalization import LotNormalizer


def test_consolidator_consolidate_stub():
    loader = SpreadsheetLoader()
    normalizer = LotNormalizer()
    consolidator = Consolidator(loader, normalizer)

    with pytest.raises(NotImplementedError):
        consolidator.consolidate(["prod.xlsx", "ship.xlsx"])
