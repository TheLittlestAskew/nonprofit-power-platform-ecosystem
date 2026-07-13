#!/usr/bin/env python3
"""Build a sanitized catalog of entities surfaced in the primary model-driven app.

Reads the private sitemap export of the "Davies Admin Bridge" model-driven
application and produces a **sanitized public** catalog mapping each surfaced
entity to its operational area, sitemap group, and entity family
(custom ``tr_`` / Nonprofit Accelerator / standard Microsoft / other publisher).

Output (tracked, public):
* ``dataverse/application-entity-catalog.csv``

The sitemap workbook has one worksheet per application **area**. Each worksheet
is a flattened sitemap: a plain title in column A starts a **group**, and
``Entity : <logicalname>`` cells name the entities surfaced beneath it. Only
structural metadata is read; no record-level data exists in this source.

The source lives under ``source-private/`` and is never committed. Run locally.

Usage:
    python scripts/build_application_catalog.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

try:
    import openpyxl
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write("ERROR: openpyxl is required. python -m pip install openpyxl\n")
    raise SystemExit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = REPO_ROOT / "source-private" / "Davies Admin Bridge SiteMap x.xlsx"
CATALOG_CSV = REPO_ROOT / "dataverse" / "application-entity-catalog.csv"

# Internal sitemap area name (worksheet title) -> public operational-area label.
AREA_LABELS: dict[str, str] = {
    "Finance Management": "Development Finance & Revenue",
    "Shelter Management": "Shelter & Case Management",
    "Tracking": "Outcomes, Grants & Compliance",
    "Volunteer Management": "Volunteer & Community Engagement",
    "Employee Management": "Employee & Administrative Operations",
    "Communications": "Communications & Brand",
}

# Standard first-party Dataverse tables surfaced in this app (by logical name).
STANDARD_TABLES = {
    "account", "contact", "annotation", "activitypointer", "systemuser", "team",
    "template", "emailsignature", "report", "organization", "cdm_company", "flowrun",
}

# Non-structural column-label / header tokens to ignore when finding group titles.
_NON_GROUP_PREFIXES = (
    "subarea_", "Id :", "Id:", "ResourceId", "DescriptionResourceId", "Description",
    "IntroducedVersion", "IsProfile", "ToolTip", "PassParams", "Sku", "VectorIcon",
    "Icon", "Client", "AvailableOffline", "Entity",
)


def classify_entity(logical_name: str) -> str:
    """Return the entity family for a surfaced entity's logical name."""
    n = logical_name.strip().lower()
    if n.startswith("tr_"):
        return "Custom (tr_)"
    if n.startswith("msnfp_") or n.startswith("msiati_"):
        return "Nonprofit Accelerator"
    if n.startswith("cr57f_"):
        return "Other publisher (budget solution)"
    if n in STANDARD_TABLES:
        return "Standard Microsoft"
    return "Unresolved"


def _is_group_header(cell0: str) -> bool:
    """True if column-A text starts a new sitemap group (a plain title)."""
    if not cell0 or cell0 == "Group":
        return False
    return not any(cell0.startswith(p) for p in _NON_GROUP_PREFIXES)


def parse_sitemap(source_file: Path) -> list[tuple[str, str, str, str, str]]:
    """Parse the workbook into rows of (public_area, internal_area, group, entity, family)."""
    if not source_file.exists():
        raise FileNotFoundError(
            f"source sitemap not found: {source_file}\n"
            "This file lives under source-private/ and is never committed."
        )
    wb = openpyxl.load_workbook(source_file, read_only=True, data_only=True)
    out: list[tuple[str, str, str, str, str]] = []
    try:
        for ws in wb.worksheets:
            internal = ws.title
            public = AREA_LABELS.get(internal, f"UNMAPPED: {internal}")
            current_group = None
            for raw in ws.iter_rows(values_only=True):
                if not raw:
                    continue
                c0 = str(raw[0]).strip() if raw[0] else ""
                if _is_group_header(c0):
                    current_group = c0
                for cell in raw:
                    if cell and isinstance(cell, str) and cell.strip().startswith("Entity :"):
                        ent = cell.split(":", 1)[1].strip()
                        if ent:
                            out.append((public, internal, current_group or "(ungrouped)", ent, classify_entity(ent)))
    finally:
        wb.close()
    return out


def write_csv(rows: list[tuple[str, str, str, str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Operational Area", "Internal App Area", "Group", "Entity (logical name)", "Entity Family"])
        for r in rows:
            w.writerow(r)


def main() -> int:
    try:
        rows = parse_sitemap(SOURCE_FILE)
    except FileNotFoundError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1

    write_csv(rows, CATALOG_CSV)

    unique = {r[3].lower() for r in rows}
    # Family of each unique entity (first occurrence wins; family is name-derived
    # and stable across occurrences).
    family_of: dict[str, str] = {}
    for r in rows:
        family_of.setdefault(r[3].lower(), r[4])
    fam_counts: dict[str, int] = {}
    for fam in family_of.values():
        fam_counts[fam] = fam_counts.get(fam, 0) + 1

    print(f"Entity references surfaced: {len(rows)}")
    print(f"Unique entities: {len(unique)}")
    for fam, ct in sorted(fam_counts.items()):
        print(f"  {fam}: {ct}")
    print(f"Wrote {CATALOG_CSV.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
