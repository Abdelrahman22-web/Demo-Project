# AC to Test Traceability

This matrix documents which automated tests verify each acceptance criterion (AC).
All ACs are covered by at least one test in `tests/test_acs.py`.

| AC | Description (short) | Test(s) |
|---|---|---|
| AC-1 | Load production + shipping files | `test_ac1_ac4_consolidates_and_matches_lots` |
| AC-2 | Parse mixed date types + flag bad rows | `test_ac2_standardizes_dates_and_flags_unparseable` |
| AC-3 | Canonical lot normalization + keep raw lot | `test_ac3_keeps_raw_lot_and_generates_canonical` |
| AC-4 | Match cross-file lots via canonical ID | `test_ac1_ac4_consolidates_and_matches_lots` |
| AC-5 | Flag Needs Review; exclude unless included | `test_ac5_flags_and_excludes_needs_review_by_default` |
| AC-6 | Consistent issue definition rule | `test_ac6_to_ac9_weekly_ranking_and_line_drilldown` |
| AC-7 | Weekly filter (Mon-Sun) | `test_ac6_to_ac9_weekly_ranking_and_line_drilldown` |
| AC-8 | Rank lines by issue count | `test_ac6_to_ac9_weekly_ranking_and_line_drilldown` |
| AC-9 | Drill-down from production line | `test_ac6_to_ac9_weekly_ranking_and_line_drilldown` |
| AC-10 | Group issue/defect categories | `test_ac10_to_ac12_trending_and_category_drilldown` |
| AC-11 | Trend delta vs previous week | `test_ac10_to_ac12_trending_and_category_drilldown` |
| AC-12 | Drill-down from category | `test_ac10_to_ac12_trending_and_category_drilldown` |
| AC-13 | Show shipping status + latest ship date | `test_ac13_to_ac15_shipping_status_and_problematic_shipped_flag` |
| AC-14 | Missing shipping handled with configured label | `test_ac13_to_ac15_shipping_status_and_problematic_shipped_flag` |
| AC-15 | Highlight problematic lots that already shipped | `test_ac13_to_ac15_shipping_status_and_problematic_shipped_flag` |
| AC-16 | Detect conflicting data for same canonical lot | `test_ac16_conflict_detection_includes_competing_sources` |
| AC-17 | Source traceability (file/sheet/row/raw values) | `test_ac17_traceability_fields_present` |
| AC-18 | Export weekly summary with metadata | `test_ac18_weekly_export_contains_tables_and_metadata` |
| AC-19 | Export drill-down with shipping fields | `test_ac19_drilldown_export_contains_shipping_fields` |
