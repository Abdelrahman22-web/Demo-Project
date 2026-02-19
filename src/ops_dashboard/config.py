"""Configuration models used by the app's service layer and UI.

The dataclasses in this module hold behavior knobs (issue rules, labels, and
period settings) so business logic is configurable without code edits.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AppConfig:
    """Immutable-style runtime configuration for reporting logic.

    Complexity:
    - Time: O(1) for construction and field access.
    - Space: O(1) for fixed-size scalar fields.
    """

    # Rule used to determine whether a production row counts as an "issue".
    issue_rule_text: str = "Count row as issue when line_issue is truthy (Yes/True/1)."
    # Label used when production lot has no matching shipping record.
    not_found_shipping_label: str = "Not Found / Not Shipped Yet"
    # Number of days in weekly comparison windows.
    comparison_period_days: int = 7
