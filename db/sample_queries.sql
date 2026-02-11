/* =========================================================
   Queries for Ops Unified Dashboard / Reporting
   (run individually as needed)
   ========================================================= */


/* 1) Unified Dashboard: consolidated view */
SELECT *
FROM v_lot_dashboard
ORDER BY COALESCE(last_inspection_timestamp, '1900-01-01') DESC,
         run_date DESC;


/* 2) Search: filter by Lot Number */
SELECT *
FROM v_lot_dashboard
WHERE lot_number = 'LOT-20260201-001';


/* 3) Filter: Date Range (production run date OR last inspection timestamp) */
SELECT *
FROM v_lot_dashboard
WHERE (run_date BETWEEN DATE '2026-02-01' AND DATE '2026-02-11')
   OR (last_inspection_timestamp BETWEEN TIMESTAMP '2026-02-01 00:00:00'
                                    AND TIMESTAMP '2026-02-11 23:59:59')
ORDER BY lot_number;


/* 4) Filter: Status (Passed/Failed) using last inspection result */
SELECT *
FROM v_lot_dashboard
WHERE last_inspection_result = 'pass';  -- or 'fail' / 'conditional'


/* 5) Compliance: show only non-compliant lots (RED) */
SELECT
  lot_number,
  last_inspection_result,
  latest_ship_status,
  compliance_indicator,
  has_shipped,
  has_hold
FROM v_lot_dashboard
WHERE compliance_indicator = 'RED'
ORDER BY COALESCE(last_inspection_timestamp, '1900-01-01') DESC;


/* 6) Compliance: summary counts (Green vs Red) */
SELECT
  compliance_indicator,
  COUNT(*) AS lot_count
FROM v_lot_dashboard
GROUP BY compliance_indicator
ORDER BY compliance_indicator;


/* 7) Problem lots: line issue OR failed inspection, and whether already shipped */
SELECT
  lot_number,
  line_issue_flag,
  last_inspection_result,
  has_shipped,
  last_ship_date,
  latest_ship_status,
  compliance_indicator
FROM v_lot_dashboard
WHERE line_issue_flag = TRUE
   OR last_inspection_result = 'fail'
ORDER BY has_shipped DESC,
         last_ship_date DESC NULLS LAST;


/* 8) Trending defects by week (for reports/meetings) */
SELECT
  DATE_TRUNC('week', ir.inspection_timestamp) AS week_start,
  dt.defect_name,
  SUM(di.defect_quantity) AS total_defects
FROM inspection_records ir
JOIN defect_instances di
  ON di.inspection_record_id = ir.inspection_record_id
JOIN defect_types dt
  ON dt.defect_type_id = di.defect_type_id
WHERE ir.inspection_timestamp >= NOW() - INTERVAL '56 days'
GROUP BY 1, 2
ORDER BY week_start DESC,
         total_defects DESC;


/* 9) Production lines with most issues this week */
SELECT
  pl.line_name,
  COUNT(*) FILTER (WHERE pr.line_issue_flag = TRUE) AS issue_runs,
  SUM(pr.downtime_minutes) AS total_downtime_minutes
FROM production_runs pr
JOIN production_lines pl
  ON pl.production_line_id = pr.production_line_id
WHERE pr.run_date >= (CURRENT_DATE - INTERVAL '7 days')
GROUP BY pl.line_name
ORDER BY issue_runs DESC,
         total_downtime_minutes DESC;


/* 10) Export-ready dataset (example): lots in a date range, ordered for CSV/PDF */
SELECT
  lot_number,
  run_date,
  line_name,
  part_number,
  units_planned,
  units_actual,
  downtime_minutes,
  line_issue_flag,
  primary_issue,
  last_inspection_timestamp,
  last_inspection_result,
  last_ship_date,
  latest_ship_status,
  compliance_indicator
FROM v_lot_dashboard
WHERE run_date BETWEEN DATE '2026-02-01' AND DATE '2026-02-11'
ORDER BY lot_number;

