"""
Domain dataclasses used by the scaffolding.

Each dataclass mirrors the key entities described in docs/data_design.md.
These are intentionally minimal and documented so a developer new to the
project can understand where fields map back to acceptance criteria.

No methods implement business logic; helpers should be added in
`consolidation`, `normalization`, or `reports` modules as appropriate.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class Lot:
    """Canonical lot identity used to join production/shipping/quality.

    Fields:
    - `lot_id`: canonical/normalized identifier (string). AC-3 says we must
      generate a canonical lot id from raw inputs; this is where it is stored.
    - `created_at`: optional datetime when the canonical record was created.
    - `notes`: optional human notes.
    """

    lot_id: str
    created_at: datetime | None = None
    notes: str | None = None


@dataclass
class LotAlias:
    """Tracks raw lot ID variants originating from source files.

    Fields correspond to AC-3 and AC-17 (source traceability): we store the
    original raw value plus source file and optional sheet/row references.
    """

    lot_id_raw: str
    source_system: str  # e.g., 'production', 'shipping', 'quality'
    source_file: str | None = None
    sheet_name: str | None = None
    row_number: int | None = None
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    canonical_lot_id: str | None = None  # filled after normalization


@dataclass
class ProductionRun:
    """A single production run row representing metrics and issue flags.

    This maps to AC-6 (issue flag), AC-7/AC-8 (week filtering and grouping by
    production_line), and AC-9 (drill-down by production line).
    """

    source_file: str | None
    row_number: int | None
    lot_raw: str
    canonical_lot_id: str | None
    production_line: str | None
    part_number: str | None
    run_date: date | None
    shift: str | None
    units_planned: int | None
    units_actual: int | None
    downtime_min: int | None
    line_issue_flag: bool | None
    primary_issue: str | None
    supervisor_notes: str | None


@dataclass
class ShipmentLine:
    """Represents a shipment line linking a lot to a shipment.

    Includes `ship_date` and `ship_status` to support AC-13..AC-15 and drill-down.
    """

    source_file: str | None
    row_number: int | None
    lot_raw: str
    canonical_lot_id: str | None
    qty_shipped: int | None
    ship_date: date | None
    ship_status: str | None


@dataclass
class SourceReference:
    """Small helper to capture where a row came from for traceability (AC-17).

    - `file_name`: original file name
    - `sheet_name`: optional spreadsheet sheet name
    - `row_number`: row number in the sheet (1-indexed)
    - `raw_values`: the raw row data as a mapping of column->value
    """

    file_name: str | None
    sheet_name: str | None
    row_number: int | None
    raw_values: dict[str, Any] = field(default_factory=dict)


__all__ = ["Lot", "LotAlias", "ProductionRun", "ShipmentLine", "SourceReference"]
