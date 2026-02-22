"""
Domain dataclasses used by the scaffolding.

Each dataclass mirrors the key entities described in docs/data_design.md.
These are intentionally minimal and documented so a developer new to the
project can understand where fields map back to acceptance criteria.

No methods implement business logic; helpers should be added in
`consolidation`, `normalization`, or `reports` modules as appropriate.
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any


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
    created_at: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class LotAlias:
    """Tracks raw lot ID variants originating from source files.

    Fields correspond to AC-3 and AC-17 (source traceability): we store the
    original raw value plus source file and optional sheet/row references.
    """

    lot_id_raw: str
    source_system: str  # e.g., 'production', 'shipping', 'quality'
    source_file: Optional[str] = None
    sheet_name: Optional[str] = None
    row_number: Optional[int] = None
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    canonical_lot_id: Optional[str] = None  # filled after normalization


@dataclass
class ProductionRun:
    """A single production run row representing metrics and issue flags.

    This maps to AC-6 (issue flag), AC-7/AC-8 (week filtering and grouping by
    production_line), and AC-9 (drill-down by production line).
    """

    source_file: Optional[str]
    row_number: Optional[int]
    lot_raw: str
    canonical_lot_id: Optional[str]
    production_line: Optional[str]
    part_number: Optional[str]
    run_date: Optional[date]
    shift: Optional[str]
    units_planned: Optional[int]
    units_actual: Optional[int]
    downtime_min: Optional[int]
    line_issue_flag: Optional[bool]
    primary_issue: Optional[str]
    supervisor_notes: Optional[str]


@dataclass
class ShipmentLine:
    """Represents a shipment line linking a lot to a shipment.

    Includes `ship_date` and `ship_status` to support AC-13..AC-15 and drill-down.
    """

    source_file: Optional[str]
    row_number: Optional[int]
    lot_raw: str
    canonical_lot_id: Optional[str]
    qty_shipped: Optional[int]
    ship_date: Optional[date]
    ship_status: Optional[str]


@dataclass
class SourceReference:
    """Small helper to capture where a row came from for traceability (AC-17).

    - `file_name`: original file name
    - `sheet_name`: optional spreadsheet sheet name
    - `row_number`: row number in the sheet (1-indexed)
    - `raw_values`: the raw row data as a mapping of column->value
    """

    file_name: Optional[str]
    sheet_name: Optional[str]
    row_number: Optional[int]
    raw_values: Dict[str, Any] = field(default_factory=dict)


__all__ = ["Lot", "LotAlias", "ProductionRun", "ShipmentLine", "SourceReference"]
