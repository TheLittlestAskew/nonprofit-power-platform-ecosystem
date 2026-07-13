# scripts/

Reproducible generators that read **private** source files (from
`source-private/`, never committed) and write **sanitized public** outputs into
tracked paths. Run them locally with the source present.

| Script | Reads (private) | Writes (public) |
|---|---|---|
| `build_dataverse_inventory.py` | `Entities with brief descriptions.xlsx` | `dataverse/custom-table-catalog.csv`, `dataverse/inventory-summary.md` |
| `build_application_catalog.py` | `Davies Admin Bridge SiteMap x.xlsx` | `dataverse/application-entity-catalog.csv` |

## Running

```bash
python -m pip install openpyxl
python scripts/build_dataverse_inventory.py
python scripts/build_application_catalog.py
```

Both scripts exit non-zero with a clear message if the source file or a required
column is missing. They emit **table-level metadata only** — no record-level or
operational data.

## Tests

```bash
python -m pip install pytest
python -m pytest tests/ -q
```
