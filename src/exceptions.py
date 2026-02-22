"""
Project-specific exceptions used across scaffolding modules.

Keep a small, explicit set of exceptions so callers can distinguish parsing
errors, normalization ambiguity, and consolidation conflicts.
"""

class DataQualityError(Exception):
    """Raised for rows that fail data quality checks (e.g., unparseable date).

    Instances may carry an `error_reason` attribute describing the failure.
    """


class AmbiguousLotError(Exception):
    """Raised when lot normalization yields multiple plausible candidates.

    This maps to AC-5 where rows must be flagged `Needs Review`.
    """


class ConflictDetectedError(Exception):
    """Raised when a conflicting set of rows is detected for the same lot.

    Optionally include the conflicting rows as an attribute so the UI can
    present competing source rows (AC-16).
    """
