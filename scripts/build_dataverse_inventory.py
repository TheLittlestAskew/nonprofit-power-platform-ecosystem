#!/usr/bin/env python3
"""Build a sanitized public catalog of custom ``tr_`` Dataverse tables.

This script reads a private source workbook that lists every entity in the
Dataverse environment, isolates the custom tables that use the ``tr_`` publisher
prefix, classifies each one, and writes two **sanitized public** artifacts:

* ``dataverse/custom-table-catalog.csv`` — one row per custom ``tr_`` table with
  its schema/logical name, description, and classification.
* ``dataverse/inventory-summary.md`` — a human-readable validation summary with
  counts, the classification rules, and unresolved questions.

Only table-level metadata (names, descriptions, classifications) is emitted.
No record-level or operational data is read or written.

The source workbook lives under ``source-private/`` and is **never** committed
(see ``AGENTS.md`` and ``SECURITY.md``). Run this script locally, with the
source present, to regenerate the public outputs.

Usage:
    python scripts/build_dataverse_inventory.py

Exits non-zero with a clear message if the source file or a required column is
missing.
"""
from __future__ import annotations

import csv
import datetime as _dt
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import openpyxl
except ModuleNotFoundError:  # pragma: no cover - environment guard
    sys.stderr.write(
        "ERROR: openpyxl is required. Install it with:  python -m pip install openpyxl\n"
    )
    raise SystemExit(2)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = REPO_ROOT / "source-private" / "Entities with brief descriptions.xlsx"
CATALOG_CSV = REPO_ROOT / "dataverse" / "custom-table-catalog.csv"
SUMMARY_MD = REPO_ROOT / "dataverse" / "inventory-summary.md"

CUSTOM_PREFIX = "tr_"

# Required columns in the source workbook's data sheet (case-insensitive match).
REQUIRED_COLUMNS = ("Entity", "Description", "Schema Name", "Logical Name")

# Classification labels (the four buckets required by the project spec).
CLASS_CORE = "core business table"
CLASS_SUPPORT = "process/support table"
CLASS_INTERSECT = "relationship/intersect table"
CLASS_UNCLEAR = "unclear/manual review"

# Support-token list. These tokens, when present in the *core* segment of a
# schema name (the part after ``tr_``), indicate a logging / audit / mapping /
# tracking utility table rather than a primary business entity. The list is kept
# deliberately tight and is documented in the output summary. It is a NAME-based
# heuristic and every match is flagged for human confirmation.
SUPPORT_TOKENS = ("log", "audit", "history", "mapping", "tracker", "migration", "mirgration")

# Values that carry no usable description. A literal ``N/A`` (common in the
# source export for auto-generated join tables) is treated the same as a blank
# cell so it can never masquerade as a real business description.
NO_DESCRIPTION_VALUES = frozenset({"", "n/a", "na", "none", "-"})

# Second-entity infixes that mark a **relationship/intersect (join)** table: a
# ``tr_`` table whose name embeds a reference to a *second* entity or publisher
# (``tr_<A>_<B>``). This is the Dataverse convention for many-to-many intersect
# entities. Detecting these by schema *structure* — not merely a bare ``_tr_`` —
# correctly classifies ``tr_``-published joins onto managed ``msnfp_``/``cdm_``
# entities (e.g. ``tr_msnfp_award_msnfp_indicator``) that a description-only rule
# would otherwise mislabel as core business tables.
INTERSECT_INFIXES = ("_tr_", "_msnfp_", "_msiati_", "_cdm_", "_msdyn_")

# Sensitive clinical / behavioral-health structures whose exact internal schema
# identifier is NOT published. The public catalog shows a generalized domain
# label instead, preserving the fact that the domain existed without exposing
# the precise instrument or record name. Keyed by lowercased schema name.
# This sanitization decision is documented in ``SECURITY.md`` and
# ``docs/evidence-register.md``. GAD-7 is included alongside PHQ-9 because it is
# an equivalent validated behavioral-health screening instrument.
SENSITIVE_GENERALIZATION = {
    "tr_phq9": "Behavioral-health assessment",
    "tr_gad7": "Behavioral-health assessment",
    "tr_diagnosis": "Clinical classification",
    "tr_diagnosticimpressions": "Clinical classification (diagnostic impressions)",
    "tr_mentalstatus": "Mental-status assessment",
    "tr_treatmentgoals": "Counseling treatment goals",
    "tr_medications": "Medication-management record",
    "tr_medlog": "Medication-management record",
}
GENERALIZED_PLACEHOLDER = "(generalized — schema name withheld)"


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class TableRow:
    """One entity row read from the source workbook."""

    entity: str
    description: str
    schema_name: str
    logical_name: str

    def is_custom(self) -> bool:
        """True when the schema OR logical name uses the ``tr_`` prefix.

        Both names are checked because either can carry the publisher prefix in
        an export; if either begins with ``tr_`` the table is custom.
        """
        return (
            self.schema_name.strip().lower().startswith(CUSTOM_PREFIX)
            or self.logical_name.strip().lower().startswith(CUSTOM_PREFIX)
        )


@dataclass(frozen=True)
class ClassifiedRow:
    """A custom table with its classification and the basis for it."""

    table: TableRow
    classification: str
    basis: str


# --------------------------------------------------------------------------- #
# Core logic (unit-tested)
# --------------------------------------------------------------------------- #

def has_custom_prefix(schema_name: str, logical_name: str) -> bool:
    """Return True if either name begins with the ``tr_`` publisher prefix.

    Edge cases handled: ``None``-like empties, leading/trailing whitespace, and
    mixed case. A name that merely *contains* ``tr_`` but does not *start* with
    it (e.g. ``cr57f_tr_budget_details``) is NOT a ``tr_`` custom table — it
    belongs to a different publisher and is excluded here.
    """
    for name in (schema_name, logical_name):
        if name and name.strip().lower().startswith(CUSTOM_PREFIX):
            return True
    return False


def has_usable_description(description: str) -> bool:
    """True when ``description`` is a real description (not blank / ``N/A``)."""
    return (description or "").strip().lower() not in NO_DESCRIPTION_VALUES


def is_intersect_by_structure(schema_name: str) -> bool:
    """True when the ``tr_`` schema name embeds a *second* entity reference.

    The core segment (schema minus the leading ``tr_``) is scanned for any
    :data:`INTERSECT_INFIXES` marker. A lone business entity such as
    ``tr_casemeeting`` has no such infix and is NOT an intersect; a join such as
    ``tr_bills_tr_davieslocations`` or ``tr_msnfp_award_msnfp_indicator`` does.
    Stripping the leading prefix first prevents the entity's *own* prefix from
    being mistaken for an embedded second reference.
    """
    schema = (schema_name or "").strip().lower()
    core = schema[len(CUSTOM_PREFIX):] if schema.startswith(CUSTOM_PREFIX) else schema
    return any(infix in core for infix in INTERSECT_INFIXES)


def classify_custom_table(schema_name: str, description: str) -> tuple[str, str]:
    """Classify a custom ``tr_`` table.

    Returns ``(classification, basis)``. Decision order, most-confident first:

    1. **relationship/intersect** — the schema name embeds a *second* entity
       reference (:data:`INTERSECT_INFIXES`: ``_tr_``, ``_msnfp_``, ``_msiati_``,
       ``_cdm_``, ``_msdyn_``). This is the Dataverse convention for
       many-to-many *intersect* entities (``tr_<A>_<B>``). A merely underscored
       or "relational-looking" single-entity name is **not** an intersect —
       only an embedded second-entity reference is. This is a schema-*structure*
       signal and is independent of the (often ``N/A``) description.
    2. **process/support** — the core segment (schema minus the leading
       ``tr_``) contains a documented support token (log/audit/mapping/etc.).
       Name-based heuristic; flagged for confirmation.
    3. **core business** — has a usable description and no support/intersect
       signal.
    4. **unclear/manual review** — no usable description (blank or ``N/A``), so
       the function cannot be verified from source.
    """
    schema = (schema_name or "").strip().lower()

    # 1. Intersect: schema structure embeds a second entity reference.
    if is_intersect_by_structure(schema):
        core = schema[len(CUSTOM_PREFIX):] if schema.startswith(CUSTOM_PREFIX) else schema
        marker = next(inf for inf in INTERSECT_INFIXES if inf in core)
        return (
            CLASS_INTERSECT,
            f"relationship/intersect by schema structure (embeds '{marker.strip('_')}' entity reference)",
        )

    core = schema[len(CUSTOM_PREFIX):] if schema.startswith(CUSTOM_PREFIX) else schema

    # 2. Support/process: documented token in the core segment.
    for token in SUPPORT_TOKENS:
        if token in core:
            return CLASS_SUPPORT, f"support-token heuristic: '{token}' in name (confirm manually)"

    # 3 / 4. Core business vs unclear, decided by whether we have a usable description.
    if has_usable_description(description):
        return CLASS_CORE, "primary business entity (has description, no support/intersect signal)"
    return CLASS_UNCLEAR, "no usable description in source — needs manual review"


def public_display(schema_name: str) -> tuple[str, bool]:
    """Return ``(public_label, is_generalized)`` for a schema name.

    Sensitive clinical/behavioral-health structures resolve to a generalized
    domain label with the exact schema identifier withheld; every other table
    returns its schema name unchanged.
    """
    label = SENSITIVE_GENERALIZATION.get((schema_name or "").strip().lower())
    if label:
        return label, True
    return schema_name, False


# --------------------------------------------------------------------------- #
# Workbook reading
# --------------------------------------------------------------------------- #

def _normalize(value: object) -> str:
    """Coerce a cell value to a trimmed string, preserving Unicode."""
    if value is None:
        return ""
    return str(value).strip()


def _resolve_columns(header: tuple[object, ...]) -> dict[str, int]:
    """Map each required column name to its 0-based index, case-insensitively.

    Raises ``KeyError`` (surfaced as a clear error by the caller) if any
    required column is missing.
    """
    lookup = { _normalize(h).lower(): i for i, h in enumerate(header) }
    resolved: dict[str, int] = {}
    missing = []
    for col in REQUIRED_COLUMNS:
        idx = lookup.get(col.lower())
        if idx is None:
            missing.append(col)
        else:
            resolved[col] = idx
    if missing:
        raise KeyError(
            "source workbook is missing required column(s): "
            + ", ".join(missing)
            + f". Found columns: {[_normalize(h) for h in header]}"
        )
    return resolved


def read_rows(source_file: Path) -> list[TableRow]:
    """Read all non-empty entity rows from the source workbook.

    Raises ``FileNotFoundError`` if the source is absent and ``KeyError`` if a
    required column is missing.
    """
    if not source_file.exists():
        raise FileNotFoundError(
            f"source workbook not found: {source_file}\n"
            "This file lives under source-private/ and is never committed. "
            "Place the private source there and re-run."
        )

    wb = openpyxl.load_workbook(source_file, read_only=True, data_only=True)
    try:
        ws = wb.worksheets[0]
        row_iter = ws.iter_rows(values_only=True)
        try:
            header = next(row_iter)
        except StopIteration:
            raise KeyError("source worksheet is empty; no header row found")
        cols = _resolve_columns(header)

        rows: list[TableRow] = []
        for raw in row_iter:
            entity = _normalize(raw[cols["Entity"]]) if cols["Entity"] < len(raw) else ""
            description = _normalize(raw[cols["Description"]]) if cols["Description"] < len(raw) else ""
            schema = _normalize(raw[cols["Schema Name"]]) if cols["Schema Name"] < len(raw) else ""
            logical = _normalize(raw[cols["Logical Name"]]) if cols["Logical Name"] < len(raw) else ""
            if not any((entity, schema, logical)):
                continue  # skip fully blank rows
            rows.append(TableRow(entity, description, schema, logical))
        return rows
    finally:
        wb.close()


# --------------------------------------------------------------------------- #
# Output writers
# --------------------------------------------------------------------------- #

def build_catalog(rows: Iterable[TableRow]) -> list[ClassifiedRow]:
    """Filter to custom ``tr_`` tables and classify each. Sorted by schema name."""
    custom = [r for r in rows if r.is_custom()]
    classified = []
    for r in custom:
        classification, basis = classify_custom_table(r.schema_name, r.description)
        classified.append(ClassifiedRow(r, classification, basis))
    classified.sort(key=lambda c: c.table.schema_name.lower())
    return classified


def write_catalog_csv(classified: list[ClassifiedRow], path: Path) -> None:
    """Write the sanitized public catalog CSV (UTF-8, Unicode preserved).

    For sensitive clinical/behavioral-health structures the exact schema and
    logical names are withheld and replaced with a generalized domain label; the
    ``Public Identifier`` column records whether a row was published as-is or
    generalized. Ordinary tables publish their exact schema names unchanged.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "Entity",
                "Schema Name",
                "Logical Name",
                "Classification",
                "Classification Basis",
                "Public Identifier",
                "Description",
            ]
        )
        for c in classified:
            t = c.table
            label, generalized = public_display(t.schema_name)
            if generalized:
                writer.writerow(
                    [
                        label,
                        GENERALIZED_PLACEHOLDER,
                        GENERALIZED_PLACEHOLDER,
                        c.classification,
                        "public identifier generalized for privacy (sensitive clinical/behavioral-health structure)",
                        "generalized",
                        "",
                    ]
                )
            else:
                description = t.description if has_usable_description(t.description) else ""
                writer.writerow(
                    [
                        t.entity,
                        t.schema_name,
                        t.logical_name,
                        c.classification,
                        c.basis,
                        "as-published",
                        description,
                    ]
                )


def _counts(classified: list[ClassifiedRow]) -> dict[str, int]:
    out = {CLASS_CORE: 0, CLASS_SUPPORT: 0, CLASS_INTERSECT: 0, CLASS_UNCLEAR: 0}
    for c in classified:
        out[c.classification] += 1
    return out


def write_summary_md(
    classified: list[ClassifiedRow],
    total_rows: int,
    source_file: Path,
    path: Path,
    generated: str,
) -> None:
    """Write the validation summary Markdown."""
    counts = _counts(classified)
    total_custom = len(classified)
    support_rows = [c for c in classified if c.classification == CLASS_SUPPORT]
    unclear_rows = [c for c in classified if c.classification == CLASS_UNCLEAR]
    intersect_rows = [c for c in classified if c.classification == CLASS_INTERSECT]

    lines: list[str] = []
    lines.append("# Custom Dataverse Table Inventory — Validation Summary")
    lines.append("")
    lines.append(f"- **Source file:** `source-private/{source_file.name}` (private; not committed)")
    lines.append(f"- **Generated:** {generated}")
    lines.append(f"- **Generator:** `scripts/build_dataverse_inventory.py`")
    lines.append(f"- **Total entities scanned in source:** {total_rows}")
    lines.append(f"- **Custom `tr_` tables identified:** **{total_custom}**")
    lines.append("")
    lines.append("## Counts by Classification")
    lines.append("")
    lines.append("| Classification | Count |")
    lines.append("|---|---|")
    lines.append(f"| Core business table | {counts[CLASS_CORE]} |")
    lines.append(f"| Process/support table | {counts[CLASS_SUPPORT]} |")
    lines.append(f"| Relationship/intersect table | {counts[CLASS_INTERSECT]} |")
    lines.append(f"| Unclear / manual review | {counts[CLASS_UNCLEAR]} |")
    lines.append(f"| **Total custom `tr_`** | **{total_custom}** |")
    lines.append("")
    lines.append("## Prefix-Detection Rule")
    lines.append("")
    lines.append(
        "A row is counted as a **custom table** when its **Schema Name** OR "
        "**Logical Name** begins with `tr_` (case-insensitive, whitespace "
        "trimmed). A name that merely *contains* `tr_` but starts with a "
        "different publisher prefix (for example `cr57f_tr_budget_details`) is "
        "**excluded** — it belongs to a different publisher and is not a `tr_` "
        "custom table."
    )
    lines.append("")
    lines.append("## Classification Rules")
    lines.append("")
    lines.append("Applied in order, most-confident first:")
    lines.append("")
    lines.append(
        "1. **Relationship/intersect** — the schema name embeds a *second* "
        "entity reference (`_tr_`, `_msnfp_`, `_msiati_`, `_cdm_`, `_msdyn_`), "
        "the Dataverse convention for many-to-many *intersect* entities "
        "(`tr_<A>_<B>`). This is a schema-**structure** signal, independent of "
        "the description (these join tables usually carry an `N/A` description "
        "in source). A merely underscored or \"relational-looking\" "
        "single-entity name is **not** treated as intersect evidence — only an "
        "embedded second-entity reference is."
    )
    lines.append(
        "2. **Process/support** — the core segment (schema minus the leading "
        f"`tr_`) contains a documented support token: {', '.join('`'+t+'`' for t in SUPPORT_TOKENS)}. "
        "This is a **name-based heuristic**; every match is listed below for "
        "manual confirmation."
    )
    lines.append(
        "3. **Core business** — has a non-empty source description and no "
        "support or intersect signal."
    )
    lines.append(
        "4. **Unclear / manual review** — no usable description (blank or `N/A`) "
        "in source, so the table's function cannot be verified here."
    )
    lines.append("")

    # Sensitive clinical/behavioral-health structures whose exact schema names
    # are withheld from this public summary.
    generalized_rows = [
        c for c in classified if public_display(c.table.schema_name)[1]
    ]
    lines.append("## Privacy Sanitization — Generalized Clinical Structures")
    lines.append("")
    lines.append(
        "The following custom tables model especially sensitive clinical or "
        "behavioral-health domains. Their exact internal schema identifiers are "
        "**withheld** from this public summary and the catalog CSV; a "
        "generalized domain label is published instead so the case study can "
        "document that the domain existed without exposing the precise "
        "instrument or record name. This decision is recorded in `SECURITY.md` "
        "and `docs/evidence-register.md`."
    )
    lines.append("")
    lines.append(f"**Generalized structures ({len(generalized_rows)}):**")
    lines.append("")
    for label in sorted({public_display(c.table.schema_name)[0] for c in generalized_rows}):
        lines.append(f"- {label}")
    lines.append("")

    lines.append("## Rows Flagged for Manual Review")
    lines.append("")
    lines.append(
        f"**Relationship/intersect candidates ({len(intersect_rows)})** — "
        "confident by schema structure, but confirm each is a true N:N intersect:"
    )
    lines.append("")
    for c in intersect_rows:
        label, generalized = public_display(c.table.schema_name)
        lines.append(f"- {label}" if generalized else f"- `{c.table.schema_name}`")
    lines.append("")
    lines.append(
        f"**Support-token heuristic matches ({len(support_rows)})** — confirm "
        "whether each is genuinely a process/support table vs. a business table:"
    )
    lines.append("")
    for c in support_rows:
        label, generalized = public_display(c.table.schema_name)
        if generalized:
            lines.append(f"- {label} — process/support (schema name generalized for privacy)")
        else:
            lines.append(f"- `{c.table.schema_name}` — {c.basis}")
    lines.append("")
    lines.append(f"**Unclear / no description ({len(unclear_rows)})**:")
    lines.append("")
    if unclear_rows:
        for c in unclear_rows:
            label, generalized = public_display(c.table.schema_name)
            lines.append(f"- {label}" if generalized else f"- `{c.table.schema_name}`")
    else:
        lines.append("- None. Every custom `tr_` table had a description in source.")
    lines.append("")
    lines.append("## Unresolved Questions")
    lines.append("")
    lines.append(
        "- Are all support-token matches truly utility tables, or are some "
        "primary business entities whose names happen to contain a token "
        "(e.g. a medication log)?"
    )
    lines.append(
        "- Do any *core business* tables actually function as intersect tables "
        "without embedding a second-entity reference in their schema name?"
    )
    lines.append(
        "- The unclear rows have no usable source description; `tr_ActionItem` "
        "in particular carries no description (`N/A`) in the revised source and "
        "remains unverified. They are reported here exactly and not "
        "force-classified to shrink the count."
    )
    lines.append(
        "- This inventory reflects the source workbook only; it is not a live "
        "read of the environment and may lag later schema changes."
    )
    lines.append("")
    lines.append(
        "_This summary contains table-level metadata only. No record-level or "
        "operational data is included._"
    )
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main() -> int:
    try:
        rows = read_rows(SOURCE_FILE)
    except FileNotFoundError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1
    except KeyError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1

    classified = build_catalog(rows)
    generated = _dt.date.today().isoformat()

    write_catalog_csv(classified, CATALOG_CSV)
    write_summary_md(classified, len(rows), SOURCE_FILE, SUMMARY_MD, generated)

    counts = _counts(classified)
    print(f"Scanned {len(rows)} entities; found {len(classified)} custom tr_ tables.")
    print(
        "  core={core}  support={support}  intersect={intersect}  unclear={unclear}".format(
            core=counts[CLASS_CORE],
            support=counts[CLASS_SUPPORT],
            intersect=counts[CLASS_INTERSECT],
            unclear=counts[CLASS_UNCLEAR],
        )
    )
    print(f"Wrote {CATALOG_CSV.relative_to(REPO_ROOT)}")
    print(f"Wrote {SUMMARY_MD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
