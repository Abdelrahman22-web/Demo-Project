"""
Top-level package for the reporting scaffolding.

This package contains only scaffolding: dataclasses, service classes, and
function stubs required by the user story acceptance criteria. No business
logic is implemented here — each function raises `NotImplementedError` so
it's obvious where to add behavior later.
"""

__all__ = [
    "models",
    "parsers",
    "normalization",
    "consolidation",
    "reports",
    "drilldown",
    "exporter",
    "exceptions",
]
