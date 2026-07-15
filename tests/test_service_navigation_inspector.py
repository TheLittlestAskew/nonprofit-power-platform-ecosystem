"""Unit tests for the service-navigation source inspector.

All fixtures are INVENTED. Fixture workbooks are built on the fly with
openpyxl and seeded with planted leakage values (a fictional organization
name, a non-reserved email, a phone-like number, a GUID, a checksum-like
base64 run, a URL, and a street address). The tests prove none of those
values can appear in the inspector's output — the inspector is safe by
construction.

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from openpyxl import Workbook

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import inspect_service_navigation as isn  # noqa: E402

# --------------------------------------------------------------------------- #
# Planted values that must NEVER appear in any inspector output.
# --------------------------------------------------------------------------- #
PLANTED_ORG = "Fictional Org Alpha"
PLANTED_ORG_2 = "Fictional Org Beta"
PLANTED_EMAIL = "leak.test@fixture-example.org"
PLANTED_PHONE = "555-123-4567"
PLANTED_GUID = "12345678-1234-1234-1234-123456789abc"
PLANTED_CHECKSUM = "QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZnaGlqaw=="
PLANTED_URL = "https://fixture-example.org/secret-path"
PLANTED_ADDRESS = "123 Fixture Street"
PLANTED_SERVICE = "Fictional confidential service text"
PLANTED_TIMESTAMP = "2026-04-16 19:53:43"

ALL_PLANTED = (
    PLANTED_ORG, PLANTED_ORG_2, PLANTED_EMAIL, PLANTED_PHONE, PLANTED_GUID,
    PLANTED_CHECKSUM, PLANTED_URL, PLANTED_ADDRESS, PLANTED_SERVICE,
    PLANTED_TIMESTAMP,
)

# Invented headers chosen to exercise the keyword classifier without
# reproducing any production header vocabulary verbatim.
DIRECTORY_HEADER = (
    "(Do Not Modify) Sample Key", "(Do Not Modify) Row Checksum",
    "(Do Not Modify) Modified On", "Sample Copy Column",
    "Sample Program Column", "Sample Organization Column",
    "Sample Rating Column", "Sample Categories Column",
    "Sample Specialization Column", "Sample Services Column",
    "Sample Phone Column", "Sample Email Column", "Sample Address Column",
    "Sample Website Column", "Sample Hours Column", "Sample About Column",
)

PATHWAY_HEADER = (
    "(Do Not Modify) Sample Key", "(Do Not Modify) Row Checksum",
    "(Do Not Modify) Modified On", "Sample ID Column", "Sample Type Column",
    "Sample Resource Column", "Sample Name Column",
    "Sample Description Column", "Sample Goal Description Column",
    "Sample Note Column", "Sample Website Column", "Sample Phone Column",
    "Sample Phase Column", "Sample Application Column", "Sample Form Column",
    "Sample Why Column", "Sample Optional Column",
)


def _directory_row(org: str, categories: str, service: str = PLANTED_SERVICE):
    return (
        PLANTED_GUID, PLANTED_CHECKSUM, PLANTED_TIMESTAMP, "",
        "Fictional Program", org, 4, categories, "Fictional focus", service,
        PLANTED_PHONE, PLANTED_EMAIL, PLANTED_ADDRESS, PLANTED_URL,
        "Fictional hours", "Fictional about text",
    )


def _pathway_row(code: str, step_type: str, resource: str = "", optional: str = ""):
    return (
        PLANTED_GUID, PLANTED_CHECKSUM, PLANTED_TIMESTAMP, code, step_type,
        resource, "Fictional step title", "Fictional description",
        "Fictional goal description", "Fictional note", PLANTED_URL,
        PLANTED_PHONE, "P1", "Fictional application", "Fictional form",
        "Fictional why", optional,
    )


def _write_book(path: Path, header: tuple, rows: list[tuple]) -> Path:
    book = Workbook()
    sheet = book.active
    sheet.title = "Fixture Data"
    sheet.append(list(header))
    for row in rows:
        sheet.append(list(row))
    hidden = book.create_sheet("fixtureHidden")
    hidden.append([f"fixture-hidden:{PLANTED_CHECKSUM}"])
    book.save(path)
    return path


@pytest.fixture()
def directory_book(tmp_path):
    rows = [
        _directory_row(PLANTED_ORG, "Cat A"),
        _directory_row(PLANTED_ORG, "Cat A; Cat B"),          # duplicate org, multi-category
        _directory_row(PLANTED_ORG_2, "Cat B", "Other fictional service"),
        _directory_row("  fictional   org  ALPHA ", "Cat C"),  # normalizes to PLANTED_ORG
        ("", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""),  # blank row
        (PLANTED_GUID, PLANTED_CHECKSUM),                       # malformed short row
    ]
    return _write_book(tmp_path / "fixture-directory.xlsx", DIRECTORY_HEADER, rows)


@pytest.fixture()
def pathway_book(tmp_path):
    rows = [
        _pathway_row("1", "Goal", resource="Fictional Resource Ref"),
        _pathway_row("1.1", "Action Items", resource="Fictional Resource Ref", optional="No"),
        _pathway_row("1.1.1", "Need", resource="Other Fictional Ref"),
        _pathway_row("1.1.2", "Need"),
        _pathway_row("1.2", "Action Items", optional="Yes"),
        _pathway_row("2", "Goal"),
        _pathway_row("2.1.1a", "Need"),
        _pathway_row("", "Mystery Type"),                      # unrecognized + blank code
    ]
    return _write_book(tmp_path / "fixture-pathway.xlsx", PATHWAY_HEADER, rows)


def _full_report(book_path: Path, analyzer) -> str:
    sheets, header, rows, blank = isn.load_sheet(book_path)
    analysis = analyzer(header, rows)
    lines = isn.render_file_report("Fixture", book_path, sheets, blank, analysis)
    if analyzer is isn.analyze_directory:
        lines += isn.render_directory_aggregates(analysis)
    else:
        lines += isn.render_pathway_aggregates(analysis)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Leakage: planted values must never appear in output.
# --------------------------------------------------------------------------- #

def test_directory_report_leaks_nothing(directory_book):
    report = _full_report(directory_book, isn.analyze_directory)
    for planted in ALL_PLANTED:
        assert planted not in report
    # case-insensitive too: no fragment of the org name survives
    assert "alpha" not in report.lower()
    assert "fixture-example" not in report.lower()


def test_pathway_report_leaks_nothing(pathway_book):
    report = _full_report(pathway_book, isn.analyze_pathway)
    for planted in ALL_PLANTED:
        assert planted not in report
    assert "fictional resource ref" not in report.lower()


def test_raw_headers_are_withheld(directory_book):
    report = _full_report(directory_book, isn.analyze_directory)
    for raw in DIRECTORY_HEADER:
        assert raw not in report


# --------------------------------------------------------------------------- #
# The output guard rejects each leakage family and allows the hash line.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("bad", [
    f"innocent label {PLANTED_EMAIL}",
    f"innocent label {PLANTED_GUID}",
    f"innocent label {PLANTED_URL}",
    f"innocent label {PLANTED_PHONE}",
    f"innocent label {PLANTED_CHECKSUM}",
    "innocent label www.fixture-example.org",
    "digits 12345678901",
])
def test_guard_rejects_leakage(bad):
    with pytest.raises(isn.LeakageError):
        isn.guard_line(bad)


def test_guard_allows_hash_and_plain_lines():
    assert isn.guard_line("  sha256=" + "ab" * 32).endswith("ab" * 32)
    assert isn.guard_line("  analyzed rows: 204 (blank rows excluded: 0)")


def test_guard_rejects_hex_run_not_in_hash_form():
    with pytest.raises(isn.LeakageError):
        isn.guard_line("stray " + "ab" * 32)


# --------------------------------------------------------------------------- #
# Aggregate correctness.
# --------------------------------------------------------------------------- #

def test_directory_aggregates(directory_book):
    _, header, rows, blank = isn.load_sheet(directory_book)
    assert blank == 1                       # the all-empty row is excluded
    assert len(rows) == 5                   # 4 real + 1 malformed short row kept
    analysis = isn.analyze_directory(header, rows)
    assert analysis["rows"] == 5
    assert analysis["org_populated"] == 4
    assert analysis["org_distinct"] == 2    # whitespace/case variant folds into Alpha
    assert analysis["org_duplicated"] == 1
    assert analysis["org_duplicate_extra_rows"] == 2
    assert analysis["service_distinct_trim"] == 2
    assert analysis["category_distinct"] == 3          # cat a, cat b, cat c
    assert analysis["category_multi_rows"] == 1
    assert analysis["category_populated"] == 4


def test_duplicate_normalization_is_deterministic(directory_book):
    _, header, rows, _ = isn.load_sheet(directory_book)
    first = isn.analyze_directory(header, rows)
    second = isn.analyze_directory(header, rows)
    assert first == second


def test_pathway_aggregates_reconcile(pathway_book):
    _, header, rows, blank = isn.load_sheet(pathway_book)
    assert blank == 0
    analysis = isn.analyze_pathway(header, rows)
    assert analysis["rows"] == 8
    assert analysis["type_counts"]["Goal"] == 2
    assert analysis["type_counts"]["Action Item"] == 2   # plural source label normalized
    assert analysis["type_counts"]["Need"] == 3
    assert analysis["unrecognized_types"] == 1
    assert analysis["reconciles"] is True                # 2+2+3+1 == 8
    assert analysis["linked_rows"] == 3
    assert analysis["linked_distinct_resources"] == 2
    assert analysis["optional_yes"] == 1
    assert analysis["optional_no"] == 1
    assert analysis["top_level_codes"] == 2
    assert analysis["code_shapes_by_type"]["Goal"] == {"#": 2}
    assert analysis["code_shapes_by_type"]["Need"] == {"#.#.#": 2, "#.#.#A": 1}
    assert analysis["code_shapes_by_type"]["<unrecognized>"] == {"<empty>": 1}


def test_malformed_short_rows_are_safe(directory_book):
    # openpyxl pads short rows on read, so feed a genuinely ragged row directly.
    _, header, rows, _ = isn.load_sheet(directory_book)
    ragged = rows + [(PLANTED_GUID, PLANTED_CHECKSUM), ()]
    analysis = isn.analyze_directory(header, ragged)    # must not raise
    assert analysis["rows"] == len(ragged)
    pathway_analysis = isn.analyze_pathway(header, ragged)  # wrong-shape sheet: still safe
    assert pathway_analysis["rows"] == len(ragged)


# --------------------------------------------------------------------------- #
# Helpers.
# --------------------------------------------------------------------------- #

def test_normalize_value_edges():
    assert isn.normalize_value(None) is None
    assert isn.normalize_value("   ") is None
    assert isn.normalize_value("  Two   Words ") == "two words"
    assert isn.normalize_value(7) == "7"


def test_code_shape_edges():
    assert isn.code_shape(None) == "<empty>"
    assert isn.code_shape("  ") == "<empty>"
    assert isn.code_shape("1.2.3") == "#.#.#"
    assert isn.code_shape("2.1.1a") == "#.#.#A"
    long_shape = isn.code_shape("word " * 20)
    assert len(long_shape) <= 17            # truncated, cannot leak long structure


def test_classify_header_unknown_and_blank():
    name, category = isn.classify_header("Zzz Mystery", 7)
    assert name == "unclassified-column-7"
    assert category == isn.CAT_TEXT
    name, _ = isn.classify_header(None, 3)
    assert name == "unclassified-column-3"


def test_find_sources_identifies_books(directory_book, pathway_book, tmp_path):
    directory, pathway = isn.find_sources(tmp_path)
    assert directory.name == "fixture-directory.xlsx"
    assert pathway.name == "fixture-pathway.xlsx"


def test_find_sources_requires_exactly_two(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        isn.find_sources(empty)
