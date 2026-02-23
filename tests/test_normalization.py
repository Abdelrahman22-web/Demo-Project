"""Unit test stubs for normalization logic.

Tests should eventually assert canonical forms and ambiguous-candidate
behavior for `LotNormalizer`. For now they confirm the function is a stub.
"""

import pytest

from src import normalization


def test_canonicalize_lot_id_stub():
    with pytest.raises(NotImplementedError):
        normalization.canonicalize_lot_id("LOT-123 a")


def test_lot_normalizer_stub():
    normalizer = normalization.LotNormalizer()
    with pytest.raises(NotImplementedError):
        normalizer.normalize("LOT-123")
