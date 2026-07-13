# tests/

Unit tests for the sanitized-catalog generators in [`../scripts/`](../scripts/).

All fixtures are **invented**. No production data is used in any test.

`test_inventory_classification.py` covers:

- `tr_` prefix detection (including exclusion of other-publisher names like
  `cr57f_tr_budget_details`)
- classification into the four buckets (core / support / intersect / unclear)
- catalog assembly (filter + sort + counts)
- required-column validation

## Running

```bash
python -m pip install pytest openpyxl
python -m pytest tests/ -q
```
