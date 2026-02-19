"""Top-level package for the operations weekly summary application.

This module exposes common configuration and service entry points so callers can
import a small, stable API surface from one place.
"""

from ops_dashboard.config import AppConfig
from ops_dashboard.consolidation import consolidate_logs
from ops_dashboard.reporting import ReportingService

__all__ = ["AppConfig", "consolidate_logs", "ReportingService"]
