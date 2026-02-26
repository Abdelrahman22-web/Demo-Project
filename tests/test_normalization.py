"""Unit test stubs for normalization logic.

Tests should eventually assert canonical forms and ambiguous-candidate
behavior for `LotNormalizer`. For now they confirm the function is a stub.
"""

from src import normalization


def test_canonicalize_lot_id_normalizes_whitespace_and_case():
    """Verify canonicalize_lot_id normalizes whitespace, case, and separators."""
    # Test basic normalization: whitespace becomes hyphen, case uppercase
    assert normalization.canonicalize_lot_id("LOT-123 a") == "LOT-123-A"

    # Test uppercase conversion
    assert normalization.canonicalize_lot_id("lot-123") == "LOT-123"

    # Test whitespace stripping
    assert normalization.canonicalize_lot_id("  LOT-456  ") == "LOT-456"

    # Test underscore normalization
    assert normalization.canonicalize_lot_id("LOT_789") == "LOT-789"

    # Test space conversion to hyphen
    assert normalization.canonicalize_lot_id("LOT 999") == "LOT-999"

    # Test invalid/empty inputs
    assert normalization.canonicalize_lot_id("") is None
    assert normalization.canonicalize_lot_id(None) is None
    assert normalization.canonicalize_lot_id("   ") is None


def test_lot_normalizer_returns_single_candidate_when_unambiguous():
    """Verify LotNormalizer.normalize returns list with single candidate."""
    normalizer = normalization.LotNormalizer()

    # Test unambiguous normalization
    result = normalizer.normalize("LOT-123")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == "LOT-123"

    # Test with whitespace and case
    result = normalizer.normalize("  lot 456  ")
    assert len(result) == 1
    assert result[0] == "LOT-456"

    # Test empty/invalid input returns empty list
    result = normalizer.normalize("")
    assert result == []

    result = normalizer.normalize("   ")
    assert result == []
