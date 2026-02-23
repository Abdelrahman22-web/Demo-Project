"""
Normalization helpers for Lot ID canonicalization.

This module contains the canonicalization API required by AC-3 and AC-4.
It intentionally exposes a small surface: a single `canonicalize_lot_id`
function and a `LotNormalizer` service stub for richer workflows.
"""



def canonicalize_lot_id(raw: str) -> str | None:
    """Return a canonical lot id for a raw input string.

    Requirements to satisfy (AC-3):
    - Normalize whitespace, hyphens, underscores, and case differences.
    - Handle common typos (e.g., replace letter 'O' vs digit '0' where safe).
    - Return `None` if the input is clearly invalid / cannot be normalized.

    NOTE: This is a stub. The function should be deterministic and idempotent.
    """

    raise NotImplementedError(
        "canonicalize_lot_id must be implemented to normalize lot identifiers"
    )


class LotNormalizer:
    """Service wrapper for canonicalization workflows.

    Responsibilities:
    - Provide batch normalization utilities.
    - Track ambiguous results (AC-5) and return candidates when ambiguous.
    - Expose configuration for typo rules and normalization steps.

    The implementation should avoid writing to a DB; it should only perform
    in-memory transformations and return structured results that higher-level
    services (consolidation) can persist or flag.
    """

    def __init__(self, *, allow_guessing: bool = False) -> None:
        self.allow_guessing = allow_guessing

    def normalize(self, raw: str) -> list[str]:
        """Return a list of candidate canonical ids for `raw`.

        - If normalization is unambiguous, return a single-item list.
        - If ambiguous, return multiple candidates so the caller can flag
          the record as `Needs Review` (AC-5).

        This is a stub and must be implemented.
        """

        raise NotImplementedError("LotNormalizer.normalize must be implemented")
