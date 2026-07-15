#!/usr/bin/env python3
"""Inspect the private service-navigation exports and emit **safe aggregates only**.

This reads the two private Dataverse Excel exports behind the
``service-navigation/`` module — a resource-directory workbook and a
goal-pathway workbook — and reports file hashes, worksheet names, row counts,
generalized column classifications, presence rates, duplicate counts,
normalized Type counts, aggregate category counts, and hierarchy-consistency
counts.

**No production row value is ever published.** The inspector never prints,
logs, writes, or serializes a cell value — no organization name, program name,
address, phone number, email address, URL, application instruction, Dataverse
GUID, row checksum, modified timestamp, or requirement text. Raw column
headers are also withheld: columns are reported only under their *generalized*
public field names (see ``service-navigation/data-dictionary.csv``). Every
output line passes through a leakage guard that rejects email-, GUID-, URL-,
phone-, and checksum-shaped text by construction.

The sources live under ``source-private/service-navigation/`` and are never
committed (see ``AGENTS.md`` / ``SECURITY.md``). Run locally with the sources
present.

Usage:
    python scripts/inspect_service_navigation.py

Exits non-zero with a clear message if a source is missing or unreadable.
"""
from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "source-private" / "service-navigation"

# --------------------------------------------------------------------------- #
# Output leakage guard. Every printed line must pass. This is the "safe by
# construction" gate: even a future bug that routed a cell value toward output
# would be caught here before anything is emitted.
# --------------------------------------------------------------------------- #

_LEAK_PATTERNS = (
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("guid", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
    ("url", re.compile(r"(?:https?|ftp)://|www\.", re.IGNORECASE)),
    ("phone", re.compile(r"\(?\d{3}\)?[ \-.]\d{3}[ \-.]\d{4}|\b\d{10,}\b")),
    # checksum/base64-like run (Dataverse row checksums are long base64 strings)
    ("checksum", re.compile(r"[A-Za-z0-9+/]{24,}={0,2}")),
)


class LeakageError(RuntimeError):
    """Raised when a would-be output line matches a leakage pattern."""


def guard_line(line: str) -> str:
    """Return ``line`` if it is safe to emit; raise ``LeakageError`` otherwise.

    SHA-256 file hashes are the one allowed long-hex token: a line consisting
    of a labelled 64-char lowercase hex digest is permitted (a file hash is an
    aggregate file property, not a row value) — but only when it matches the
    exact ``sha256=<64 hex>`` form this script prints.
    """
    candidate = re.sub(r"\bsha256=[0-9a-f]{64}\b", "sha256=<hash>", line)
    for name, pattern in _LEAK_PATTERNS:
        if pattern.search(candidate):
            raise LeakageError(f"refusing to emit output line matching {name!r} pattern")
    return line


def emit(lines: list[str], text: str) -> None:
    """Append a guarded output line."""
    lines.append(guard_line(text))


# --------------------------------------------------------------------------- #
# Generalized column classification.
#
# Raw source headers are NEVER emitted. Each header is matched (casefolded,
# keyword rules, most-specific first) to a generalized public field name and a
# privacy category. Unrecognized headers surface as ``unclassified-column-<n>``
# so a schema change cannot silently leak a new header name.
# --------------------------------------------------------------------------- #

CAT_INTERNAL = "internal-metadata"      # GUIDs, checksums, timestamps: withheld
CAT_CONTACT = "contact-channel"         # phones, emails: presence only
CAT_LOCATION = "location"               # addresses: presence only
CAT_LINK = "web-link"                   # URLs: presence only
CAT_TAXONOMY = "taxonomy"               # categories/specializations: aggregate only
CAT_TEXT = "descriptive-text"           # free text: presence only
CAT_HIERARCHY = "hierarchy"             # codes, types, parents: aggregate/shape only
CAT_REFERENCE = "record-reference"      # lookups: link counts only
CAT_SIGNAL = "curation-signal"          # ratings/flags: aggregate only

# (keyword, public field name, category) — first match wins, order matters.
_HEADER_RULES: tuple[tuple[str, str, str], ...] = (
    ("checksum", "row_checksum", CAT_INTERNAL),
    ("modified", "modified_timestamp", CAT_INTERNAL),
    ("do not modify", "internal_identifier", CAT_INTERNAL),
    ("phone", "support_contact", CAT_CONTACT),
    ("email", "contact_email", CAT_CONTACT),
    ("address", "location", CAT_LOCATION),
    ("website", "web_link", CAT_LINK),
    ("hour", "hours_availability", CAT_TEXT),
    ("categor", "top_level_categories", CAT_TAXONOMY),
    ("specializ", "specialization", CAT_TAXONOMY),
    ("service", "service_description", CAT_TAXONOMY),
    ("organization", "organization_title", CAT_TEXT),
    ("program", "program_title", CAT_TEXT),
    ("rating", "average_rating", CAT_SIGNAL),
    ("about", "summary", CAT_TEXT),
    ("copy", "copy_target", CAT_REFERENCE),
    ("resource", "linked_resource", CAT_REFERENCE),
    ("type", "step_type", CAT_HIERARCHY),
    ("goal desc", "goal_summary", CAT_TEXT),
    ("why", "rationale", CAT_TEXT),
    ("application", "application_links", CAT_TEXT),
    ("form", "form_links", CAT_TEXT),
    ("phase", "phase", CAT_HIERARCHY),
    ("optional", "optional_step", CAT_SIGNAL),
    ("note", "note", CAT_TEXT),
    ("need", "need_text", CAT_TEXT),
    ("description", "step_summary", CAT_TEXT),
    ("id", "step_code", CAT_HIERARCHY),
    ("name", "step_title", CAT_TEXT),
)


def classify_header(header: object, position: int) -> tuple[str, str]:
    """Map a raw header to ``(public_field_name, category)``.

    The raw header text never leaves this function. Unmatched or empty headers
    classify as ``unclassified-column-<position>`` / descriptive-text so new
    source columns are visible without being named.
    """
    text = str(header).casefold().strip() if header is not None else ""
    if text:
        for keyword, public_name, category in _HEADER_RULES:
            if keyword in text:
                return public_name, category
    return f"unclassified-column-{position}", CAT_TEXT


# --------------------------------------------------------------------------- #
# Normalization + shape helpers (deterministic; documented in metrics.md).
# --------------------------------------------------------------------------- #

def normalize_value(value: object) -> str | None:
    """Trim, collapse internal whitespace, casefold. ``None`` when blank."""
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    return text.casefold() or None


def is_blank_row(row: tuple) -> bool:
    """True when every cell is empty or whitespace-only."""
    return all(cell is None or str(cell).strip() == "" for cell in row)


def code_shape(value: object, max_len: int = 16) -> str:
    """Reduce a hierarchy code to a pattern shape: digits -> ``#``, letters -> ``A``.

    Whitespace runs collapse to one space and the shape is truncated to
    ``max_len`` so free text accidentally present in a code column cannot leak
    structure. Blank cells report ``<empty>``.
    """
    if value is None or str(value).strip() == "":
        return "<empty>"
    shape = re.sub(r"\s+", " ", str(value).strip())
    shape = re.sub(r"[0-9]+", "#", shape)
    shape = re.sub(r"[A-Za-z]+", "A", shape)
    return shape[:max_len] + ("~" if len(shape) > max_len else "")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------- #
# Workbook loading + analysis. Functions accept explicit paths so tests can
# run them against entirely invented fixture workbooks.
# --------------------------------------------------------------------------- #

def load_sheet(path: Path) -> tuple[list[str], tuple, list[tuple], int]:
    """Load the primary data worksheet of an export workbook.

    Returns ``(worksheet_names, header_row, data_rows, blank_rows_excluded)``.
    The primary sheet is the one with the most data rows (each export carries a
    hidden Dataverse re-import sheet, which is skipped and never analyzed).
    Blank rows are excluded by rule. Raises ``ValueError`` on an empty workbook.
    """
    from openpyxl import load_workbook  # deferred: tests import this module cheaply

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        best: tuple[str, list[tuple]] | None = None
        for name in workbook.sheetnames:
            rows = list(workbook[name].iter_rows(values_only=True))
            if best is None or len(rows) > len(best[1]):
                best = (name, rows)
        sheet_names = list(workbook.sheetnames)
    finally:
        workbook.close()
    if best is None or not best[1]:
        raise ValueError(f"workbook has no analyzable rows: {path.name}")
    _, rows = best
    header, data = rows[0], rows[1:]
    kept = [row for row in data if not is_blank_row(row)]
    return sheet_names, header, kept, len(data) - len(kept)


def column_index(header: tuple, public_name: str) -> int | None:
    """Index of the column whose generalized classification is ``public_name``."""
    for position, raw in enumerate(header):
        name, _ = classify_header(raw, position)
        if name == public_name:
            return position
    return None


def presence_counts(header: tuple, rows: list[tuple]) -> list[tuple[str, str, int]]:
    """Per-column ``(public_field, category, populated_count)`` in header order."""
    out = []
    for position, raw in enumerate(header):
        name, category = classify_header(raw, position)
        populated = sum(
            1 for row in rows
            if position < len(row) and row[position] is not None and str(row[position]).strip()
        )
        out.append((name, category, populated))
    return out


def analyze_directory(header: tuple, rows: list[tuple]) -> dict:
    """Safe aggregates for the resource-directory sheet. No values returned."""
    org_col = column_index(header, "organization_title")
    svc_col = column_index(header, "service_description")
    cat_col = column_index(header, "top_level_categories")
    prog_col = column_index(header, "program_title")

    def cell(row: tuple, col: int | None) -> object:
        return row[col] if col is not None and col < len(row) else None

    orgs = [normalize_value(cell(r, org_col)) for r in rows]
    org_values = [o for o in orgs if o]
    org_counter = Counter(org_values)
    duplicated = {k: v for k, v in org_counter.items() if v > 1}

    services_trim = {str(cell(r, svc_col)).strip() for r in rows
                     if cell(r, svc_col) is not None and str(cell(r, svc_col)).strip()}
    services_norm = {normalize_value(cell(r, svc_col)) for r in rows
                     if normalize_value(cell(r, svc_col))}

    category_tokens: set[str] = set()
    multi_category_rows = 0
    categorized_rows = 0
    for r in rows:
        raw = cell(r, cat_col)
        if raw is None or not str(raw).strip():
            continue
        categorized_rows += 1
        tokens = [normalize_value(part) for part in str(raw).split(";")]
        tokens = [t for t in tokens if t]
        if len(tokens) > 1:
            multi_category_rows += 1
        category_tokens.update(tokens)

    programs = {normalize_value(cell(r, prog_col)) for r in rows if normalize_value(cell(r, prog_col))}

    return {
        "rows": len(rows),
        "org_populated": len(org_values),
        "org_distinct": len(org_counter),
        "org_duplicated": len(duplicated),
        "org_duplicate_extra_rows": sum(v - 1 for v in duplicated.values()),
        "service_populated": sum(1 for r in rows if cell(r, svc_col) is not None and str(cell(r, svc_col)).strip()),
        "service_distinct_trim": len(services_trim),
        "service_distinct_normalized": len(services_norm),
        "category_populated": categorized_rows,
        "category_distinct": len(category_tokens),
        "category_multi_rows": multi_category_rows,
        "program_distinct": len(programs),
        "presence": presence_counts(header, rows),
    }


# Public labels for the three hierarchy levels. The source's middle label is
# plural; normalization maps either form to the singular public label.
_TYPE_LABELS = {
    "goal": "Goal",
    "action item": "Action Item",
    "action items": "Action Item",
    "need": "Need",
}


def analyze_pathway(header: tuple, rows: list[tuple]) -> dict:
    """Safe aggregates for the goal-pathway sheet. No values returned."""
    type_col = column_index(header, "step_type")
    code_col = column_index(header, "step_code")
    link_col = column_index(header, "linked_resource")
    opt_col = column_index(header, "optional_step")
    phase_col = column_index(header, "phase")

    def cell(row: tuple, col: int | None) -> object:
        return row[col] if col is not None and col < len(row) else None

    type_counts: Counter[str] = Counter()
    shapes_by_type: dict[str, Counter] = {}
    linked_by_type: Counter[str] = Counter()
    linked_targets: set[str] = set()
    top_prefixes: set[str] = set()
    unrecognized_types = 0

    for r in rows:
        label = _TYPE_LABELS.get(normalize_value(cell(r, type_col)) or "")
        if label is None:
            unrecognized_types += 1
            label = "<unrecognized>"
        type_counts[label] += 1
        shapes_by_type.setdefault(label, Counter())[code_shape(cell(r, code_col))] += 1
        link = normalize_value(cell(r, link_col))
        if link:
            linked_by_type[label] += 1
            linked_targets.add(link)
        code = str(cell(r, code_col)).strip() if cell(r, code_col) is not None else ""
        match = re.match(r"^(\d+)", code)
        if match:
            top_prefixes.add(match.group(1))

    optional = Counter(normalize_value(cell(r, opt_col)) for r in rows)
    hierarchy_total = sum(v for k, v in type_counts.items() if k != "<unrecognized>")

    return {
        "rows": len(rows),
        "type_counts": dict(type_counts),
        "unrecognized_types": unrecognized_types,
        "reconciles": hierarchy_total + unrecognized_types == len(rows),
        "code_shapes_by_type": {k: dict(v) for k, v in shapes_by_type.items()},
        "top_level_codes": len(top_prefixes),
        "linked_rows": sum(linked_by_type.values()),
        "linked_by_type": dict(linked_by_type),
        "linked_distinct_resources": len(linked_targets),
        "optional_yes": optional.get("yes", 0),
        "optional_no": optional.get("no", 0),
        "phase_populated": sum(1 for r in rows if cell(r, phase_col) is not None and str(cell(r, phase_col)).strip()),
        "presence": presence_counts(header, rows),
    }


# --------------------------------------------------------------------------- #
# Report rendering — the only path to stdout; every line is guarded.
# --------------------------------------------------------------------------- #

def render_file_report(title: str, path: Path, sheet_names: list[str],
                       blank_excluded: int, analysis: dict) -> list[str]:
    lines: list[str] = []
    emit(lines, f"== {title} ==")
    emit(lines, f"  file: {path.name}")
    emit(lines, f"  sha256={sha256_of(path)}")
    emit(lines, f"  worksheets: {len(sheet_names)} (primary data sheet analyzed; "
                "hidden re-import metadata sheet excluded)")
    emit(lines, f"  analyzed rows: {analysis['rows']} (blank rows excluded: {blank_excluded})")
    emit(lines, "  column structure (generalized names only; raw headers withheld):")
    for name, category, populated in analysis["presence"]:
        emit(lines, f"    {name:24} {category:20} populated {populated}/{analysis['rows']}")
    return lines


def render_directory_aggregates(a: dict) -> list[str]:
    lines: list[str] = []
    emit(lines, "  aggregates:")
    emit(lines, f"    distinct organizations (normalized): {a['org_distinct']} "
                f"of {a['org_populated']} populated")
    emit(lines, f"    organizations on >1 row: {a['org_duplicated']} "
                f"(+{a['org_duplicate_extra_rows']} extra rows: legitimate multi-program shape)")
    emit(lines, f"    distinct program titles: {a['program_distinct']}")
    emit(lines, f"    distinct service descriptions: {a['service_distinct_trim']} trim-only / "
                f"{a['service_distinct_normalized']} normalized, of {a['service_populated']} populated")
    emit(lines, f"    distinct top-level categories: {a['category_distinct']} "
                f"(multi-category rows: {a['category_multi_rows']}, categorized rows: {a['category_populated']})")
    return lines


def render_pathway_aggregates(a: dict) -> list[str]:
    lines: list[str] = []
    emit(lines, "  aggregates:")
    parts = ", ".join(f"{k}: {v}" for k, v in sorted(a["type_counts"].items()))
    emit(lines, f"    step types (normalized): {parts}")
    emit(lines, f"    reconciliation: type totals {'match' if a['reconciles'] else 'DO NOT match'} "
                f"the analyzed row count ({a['rows']})")
    if a["unrecognized_types"]:
        emit(lines, f"    WARNING: {a['unrecognized_types']} row(s) with unrecognized type")
    for level, shapes in sorted(a["code_shapes_by_type"].items()):
        shaped = ", ".join(f"{shape} x{count}" for shape, count in sorted(shapes.items()))
        emit(lines, f"    hierarchy-code shapes [{level}]: {shaped}")
    emit(lines, f"    distinct top-level pathway codes: {a['top_level_codes']}")
    emit(lines, f"    rows linked to a resource: {a['linked_rows']} "
                f"({', '.join(f'{k} {v}' for k, v in sorted(a['linked_by_type'].items()))})")
    emit(lines, f"    distinct linked resources: {a['linked_distinct_resources']}")
    emit(lines, f"    optional-step flag: yes {a['optional_yes']} / no {a['optional_no']} "
                f"(blank treated as required)")
    emit(lines, f"    phase populated: {a['phase_populated']}")
    return lines


def find_sources(source_dir: Path) -> tuple[Path, Path]:
    """Locate the two exports and identify which is which by column shape.

    The pathway workbook is the one whose header classifies a ``step_type``
    column; the directory workbook is the other. Raises ``FileNotFoundError``
    unless exactly two ``.xlsx`` files are present.
    """
    books = sorted(source_dir.glob("*.xlsx"))
    if len(books) != 2:
        raise FileNotFoundError(
            f"expected exactly 2 .xlsx exports in {source_dir} "
            f"(found {len(books)}). Place the private service-navigation "
            "exports there and re-run."
        )
    first_header = load_sheet(books[0])[1]
    if column_index(first_header, "step_type") is not None:
        return books[1], books[0]
    return books[0], books[1]


def main() -> int:
    try:
        directory_path, pathway_path = find_sources(SOURCE_DIR)
        dir_sheets, dir_header, dir_rows, dir_blank = load_sheet(directory_path)
        path_sheets, path_header, path_rows, path_blank = load_sheet(pathway_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1

    directory = analyze_directory(dir_header, dir_rows)
    pathway = analyze_pathway(path_header, path_rows)

    lines: list[str] = []
    emit(lines, "No production row value is published. Only file hashes, generalized")
    emit(lines, "structure, and aggregate counts are reported.")
    emit(lines, "")
    lines += render_file_report("Resource directory export", directory_path,
                                dir_sheets, dir_blank, directory)
    lines += render_directory_aggregates(directory)
    emit(lines, "")
    lines += render_file_report("Goal pathway export", pathway_path,
                                path_sheets, path_blank, pathway)
    lines += render_pathway_aggregates(pathway)

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
