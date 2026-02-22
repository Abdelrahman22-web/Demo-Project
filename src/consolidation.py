"""
Consolidation service: load, normalize, match, and flag records.

This module provides the high-level `Consolidator` class responsible for
combining rows from multiple files into a canonical dataset as required by
AC-1 through AC-5 and AC-16..AC-17.

Only scaffolding is provided: each method documents its responsibility and
raises `NotImplementedError` so implementers can fill logic incrementally.
"""
from typing import Iterable, Dict, Any, List, Tuple
from .models import ProductionRun, ShipmentLine, SourceReference, LotAlias
from .parsers import SpreadsheetLoader
from .normalization import LotNormalizer


class ConsolidationResult:
    """Container for consolidation outcomes.

    - `rows`: consolidated rows (production/shipping) mapped to canonical ids
    - `needs_review`: list of records that were flagged as ambiguous/unparseable
    - `errors`: parsing or other errors with reasons (AC-2, AC-5)
    """

    def __init__(self):
        self.rows: List[Dict[str, Any]] = []
        self.needs_review: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []


class Consolidator:
    """Orchestrates import and consolidation logic.

    Responsibilities:
    - Use `SpreadsheetLoader` to read multiple files (AC-1).
    - Parse and coerce dates using parsing utilities (AC-2).
    - Call `LotNormalizer` to produce canonical_lot_id and LotAlias entries
      (AC-3, AC-4).
    - Match cross-file lots by canonical id and flag ambiguous cases (AC-5).
    - Detect conflicts (AC-16) when the same canonical id has conflicting
      key data (e.g., different ship_status or production_line).
    - Retain source traceability metadata for every consolidated row (AC-17).

    This class is a scaffold; concrete storage (DB) interactions are out of
    scope for this module and should be implemented by the caller.
    """

    def __init__(self, loader: SpreadsheetLoader, normalizer: LotNormalizer) -> None:
        self.loader = loader
        self.normalizer = normalizer

    def consolidate(self, file_paths: Iterable[str], *, include_flagged: bool = False) -> ConsolidationResult:
        """Run consolidation across provided `file_paths`.

        - `include_flagged`: when True, flagged rows (Needs Review) are
          included in `rows`; otherwise they are excluded per AC-5.

        Returns a `ConsolidationResult` with rows, needs_review, and errors.
        """

        raise NotImplementedError("Consolidator.consolidate must be implemented to run import + normalization + matching")

    def _detect_conflicts(self, consolidated_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Inspect consolidated rows and return detected conflicts (AC-16).

        - Should compare key fields across rows that share a canonical_lot_id
          and return structured conflict descriptions that allow showing
          competing source rows.
        """

        raise NotImplementedError("Consolidator._detect_conflicts must be implemented")
