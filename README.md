# Ops Weekly Summary

## a) Project Description
This project implements a weekly operations reporting tool for an Operations Specialist.

It consolidates Production and Shipping spreadsheets into one canonical dataset, then provides:
- Production line ranking by issue count.
- Trending issue/defect categories versus previous week.
- Drill-down to impacted lots with shipping status.
- Data quality flags (Needs Review), conflict detection, and source traceability.
- CSV/XLSX exports for weekly summary and drill-down outputs.

The implementation follows the class project stack in `docs/tech_stack_decision_records.md`:
- Python
- Streamlit
- Pandas (data/service layer)
- Pytest (tests)

## b) How To Run / Build The Code
### Prerequisites
- Python 3.11+
- Poetry (recommended)

### Install
```bash
poetry install
```

### Run Streamlit App
```bash
poetry run streamlit run streamlit_app.py
```

### Alternative (without Poetry)
```bash
pip install pandas openpyxl streamlit xlsxwriter python-dateutil pytest
streamlit run streamlit_app.py
```

## c) Usage Examples
1. Open the app.
2. Upload both files:
- Production log (`.csv`/`.xlsx`)
- Shipping log (`.csv`/`.xlsx`)
3. Configure:
- Issue Rule text (displayed to users as the rule definition).
- Missing-shipping label (for lots not found in shipping).
- Include/exclude `Needs Review` rows.
4. Pick a week anchor date.
5. Review:
- Weekly line ranking.
- Trending issue categories and deltas vs previous week.
- Line/category drill-down tables.
6. Export:
- Weekly Summary CSV/XLSX.
- Drill-down CSV.

## d) How To Run Tests
```bash
poetry run pytest -q
```

If you are not using Poetry:
```bash
pytest -q
```

## Project Structure
```text
Demo-Project/
  db/
    schema.sql
    seed.sql
    sample_queries.sql
  docs/
    data_design.md
    assumptions_scope.md
    architecture_decision_records.md
    tech_stack_decision_records.md
    ac_test_traceability.md
  src/ops_dashboard/
    __init__.py
    config.py
    io.py
    normalization.py
    consolidation.py
    reporting.py
    exporting.py
    models.py
  tests/
    conftest.py
    test_acs.py
  streamlit_app.py
  pyproject.toml
```

## Notes On Resource Safety
- Spreadsheet reads are handled by pandas, which closes file handles after read.
- XLSX export uses `with pd.ExcelWriter(...)` so workbook resources are always closed.

## Acceptance Criteria Coverage
See `docs/ac_test_traceability.md` for the full AC-1..AC-19 mapping to tests.
