"""Unit tests for the service-navigation source inspector.

All fixtures are INVENTED. Fixture workbooks are built on the fly with
openpyxl and seeded with planted leakage values (a fictional organization
name, a non-reserved email, a phone-like number, a GUID, a checksum-like
base64 run, a URL, a street address, and a distinctive private filename).
The tests prove none of those values can appear in the inspector's output —
the inspector is safe by construction.

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
# Distinctive private filename parts (a real export embeds terminology + a
# timestamp in its name). Letters only, so a hex hash can never contain it.
PLANTED_FILENAME = "zzsecretexportzz 9-9-2099.xlsx"

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

MINI_PATHWAY_HEADER = ("Sample Type Column", "Sample ID Column",
                       "Sample Resource Column", "Sample Optional Column")
MINI_DIRECTORY_HEADER = ("Sample Program Column", "Sample Organization Column",
                         "Sample Categories Column", "Sample Services Column")


def _directory_row(org: str, categories: str, service: str = PLANTED_SERVICE,
                   program: str = "Fictional Program"):
    return (
        PLANTED_GUID, PLANTED_CHECKSUM, PLANTED_TIMESTAMP, "",
        program, org, 4, categories, "Fictional focus", service,
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


def _write_book(path: Path, sheets: list[tuple[str, tuple, list[tuple], str]]) -> Path:
    """Write a workbook. ``sheets`` is [(title, header, rows, state), ...]."""
    book = Workbook()
    book.remove(book.active)
    for title, header, rows, state in sheets:
        sheet = book.create_sheet(title)
        sheet.append(list(header))
        for row in rows:
            sheet.append(list(row))
        sheet.sheet_state = state
    book.save(path)
    return path


DIRECTORY_ROWS = [
    _directory_row(PLANTED_ORG, "Cat A"),
    _directory_row(PLANTED_ORG, "Cat A; Cat B", program="Fictional Program Two"),
    _directory_row(PLANTED_ORG_2, "Cat B", "Other fictional service"),
    _directory_row("  fictional   org  ALPHA ", "Cat C"),  # normalizes to PLANTED_ORG
    ("", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""),  # blank row
]

PATHWAY_ROWS = [
    _pathway_row("1", "Goal", resource="Fictional Resource Ref"),
    _pathway_row("1.1", "Action Items", resource="Fictional Resource Ref", optional="No"),
    _pathway_row("1.1.1", "Need", resource="Other Fictional Ref"),
    _pathway_row("1.1.2", "Need"),
    _pathway_row("1.2", "Action Items", optional="Yes"),
    _pathway_row("2", "Goal"),
    _pathway_row("2.1.1a", "Need"),          # valid letter-suffix code, parent missing
    _pathway_row("", "Mystery Type"),        # unrecognized type + blank code
]


@pytest.fixture()
def directory_book(tmp_path):
    return _write_book(tmp_path / "fixture-directory.xlsx", [
        ("Fixture Data", DIRECTORY_HEADER, DIRECTORY_ROWS, "visible"),
        ("fixtureHidden", (f"fixture-hidden:{PLANTED_CHECKSUM}",), [], "hidden"),
    ])


@pytest.fixture()
def pathway_book(tmp_path):
    return _write_book(tmp_path / "fixture-pathway.xlsx", [
        ("Fixture Data", PATHWAY_HEADER, PATHWAY_ROWS, "visible"),
        ("fixtureHidden", (f"fixture-hidden:{PLANTED_CHECKSUM}",), [], "hidden"),
    ])


def _full_report(book_path: Path) -> str:
    export = isn.load_export(book_path)
    if export["role"] == isn.ROLE_DIRECTORY:
        analysis = isn.analyze_directory(export["header"], export["rows"])
        lines = isn.render_file_report(book_path, export, analysis)
        lines += isn.render_directory_aggregates(analysis)
    else:
        analysis = isn.analyze_pathway(export["header"], export["rows"])
        lines = isn.render_file_report(book_path, export, analysis)
        lines += isn.render_pathway_aggregates(analysis)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Leakage: planted values must never appear in output.
# --------------------------------------------------------------------------- #

def test_directory_report_leaks_nothing(directory_book):
    report = _full_report(directory_book)
    for planted in ALL_PLANTED:
        assert planted not in report
    assert "alpha" not in report.lower()
    assert "fixture-example" not in report.lower()


def test_pathway_report_leaks_nothing(pathway_book):
    report = _full_report(pathway_book)
    for planted in ALL_PLANTED:
        assert planted not in report
    assert "fictional resource ref" not in report.lower()


def test_raw_headers_are_withheld(directory_book):
    report = _full_report(directory_book)
    for raw in DIRECTORY_HEADER:
        assert raw not in report


def test_private_filename_never_in_output(tmp_path):
    """A distinctive private filename (terminology + embedded export date)
    must not appear in the rendered report."""
    book = _write_book(tmp_path / PLANTED_FILENAME, [
        ("Fixture Data", DIRECTORY_HEADER, DIRECTORY_ROWS, "visible"),
    ])
    report = _full_report(book)
    assert "zzsecretexportzz" not in report.lower()
    assert "9-9-2099" not in report
    assert PLANTED_FILENAME not in report
    assert str(tmp_path) not in report          # no private path either


def test_join_render_leaks_nothing(directory_book, pathway_book):
    directory_export = isn.load_export(directory_book)
    pathway_export = isn.load_export(pathway_book)
    pathway = isn.analyze_pathway(pathway_export["header"], pathway_export["rows"])
    join = isn.join_resource_references(directory_export["header"],
                                        directory_export["rows"],
                                        pathway["linked_values"])
    report = "\n".join(isn.render_join(join))
    for planted in ALL_PLANTED:
        assert planted not in report
    assert "fictional" not in report.lower()    # no reference value survives


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
# Worksheet selection: visibility + schema, never row count.
# --------------------------------------------------------------------------- #

def test_hidden_sheet_with_more_rows_is_excluded(tmp_path):
    """A hidden metadata sheet larger than the data sheet must not be picked,
    even when it carries a matching schema."""
    many = [_directory_row(PLANTED_ORG, "Cat X") for _ in range(50)]
    book = _write_book(tmp_path / "fixture.xlsx", [
        ("Hidden Big", DIRECTORY_HEADER, many, "hidden"),
        ("Visible Small", DIRECTORY_HEADER, DIRECTORY_ROWS, "visible"),
    ])
    export = isn.load_export(book)
    assert export["role"] == isn.ROLE_DIRECTORY
    assert len(export["rows"]) == 4             # visible sheet's rows (blank excluded)


def test_two_matching_visible_sheets_is_ambiguous(tmp_path):
    book = _write_book(tmp_path / "fixture.xlsx", [
        ("First", DIRECTORY_HEADER, DIRECTORY_ROWS, "visible"),
        ("Second", DIRECTORY_HEADER, DIRECTORY_ROWS, "visible"),
    ])
    with pytest.raises(ValueError, match="ambiguous"):
        isn.load_export(book)


def test_no_matching_visible_sheet_errors(tmp_path):
    book = _write_book(tmp_path / "fixture.xlsx", [
        ("Junk", ("Zzz One", "Zzz Two"), [("a", "b")], "visible"),
        ("HiddenMatch", DIRECTORY_HEADER, DIRECTORY_ROWS, "hidden"),
    ])
    with pytest.raises(ValueError, match="no visible worksheet"):
        isn.load_export(book)


def test_correct_visible_sheet_selected(directory_book):
    export = isn.load_export(directory_book)
    assert export["role"] == isn.ROLE_DIRECTORY
    assert export["sheet_count"] == 2
    assert export["blank_excluded"] == 1
    assert len(export["rows"]) == 4


# --------------------------------------------------------------------------- #
# Aggregate correctness.
# --------------------------------------------------------------------------- #

def test_directory_aggregates(directory_book):
    export = isn.load_export(directory_book)
    analysis = isn.analyze_directory(export["header"], export["rows"])
    assert analysis["rows"] == 4
    assert analysis["org_populated"] == 4
    assert analysis["org_distinct"] == 2        # whitespace/case variant folds into Alpha
    assert analysis["org_repeated"] == 1
    assert analysis["org_repeated_extra_rows"] == 2
    assert analysis["service_distinct_trim"] == 2
    assert analysis["category_distinct"] == 3   # cat a, cat b, cat c
    assert analysis["category_multi_rows"] == 1
    assert analysis["category_populated"] == 4
    assert analysis["program_populated"] == 4
    assert analysis["program_distinct"] == 2


def test_repeated_org_with_multiple_programs_counted(directory_book):
    export = isn.load_export(directory_book)
    analysis = isn.analyze_directory(export["header"], export["rows"])
    # Alpha appears 3x with two distinct program titles -> counted once.
    assert analysis["org_repeated_with_multiple_programs"] == 1


def test_repeated_org_with_single_program_not_counted():
    rows = [
        ("Fictional Prog", PLANTED_ORG, "Cat A", "Svc"),
        ("Fictional Prog", PLANTED_ORG, "Cat A", "Svc"),
    ]
    analysis = isn.analyze_directory(MINI_DIRECTORY_HEADER, rows)
    assert analysis["org_repeated"] == 1
    assert analysis["org_repeated_with_multiple_programs"] == 0


def test_duplicate_normalization_is_deterministic(directory_book):
    export = isn.load_export(directory_book)
    first = isn.analyze_directory(export["header"], export["rows"])
    second = isn.analyze_directory(export["header"], export["rows"])
    assert first == second


def test_pathway_aggregates(pathway_book):
    export = isn.load_export(pathway_book)
    analysis = isn.analyze_pathway(export["header"], export["rows"])
    assert analysis["rows"] == 8
    assert analysis["type_counts"]["Goal"] == 2
    assert analysis["type_counts"]["Action Item"] == 2   # plural source label normalized
    assert analysis["type_counts"]["Need"] == 3
    assert analysis["unrecognized_types"] == 1
    assert analysis["linked_rows"] == 3
    assert analysis["linked_distinct_resources"] == 2
    assert analysis["top_level_codes"] == 2
    assert analysis["code_shapes_by_type"]["Need"] == {"#.#.#": 2, "#.#.#A": 1}


def test_malformed_short_rows_are_safe(directory_book):
    # openpyxl pads short rows on read, so feed a genuinely ragged row directly.
    export = isn.load_export(directory_book)
    ragged = export["rows"] + [(PLANTED_GUID, PLANTED_CHECKSUM), ()]
    analysis = isn.analyze_directory(export["header"], ragged)      # must not raise
    assert analysis["rows"] == len(ragged)
    pathway_analysis = isn.analyze_pathway(export["header"], ragged)  # wrong-shape sheet: still safe
    assert pathway_analysis["rows"] == len(ragged)


# --------------------------------------------------------------------------- #
# Reconciliation: real, not tautological.
# --------------------------------------------------------------------------- #

def _mini_pathway(rows):
    return isn.analyze_pathway(MINI_PATHWAY_HEADER, rows)


def test_reconciliation_true_when_all_recognized():
    rows = [("Goal", "1", "", ""), ("Action Items", "1.1", "", ""), ("Need", "1.1.1", "", "")]
    analysis = _mini_pathway(rows)
    assert analysis["unrecognized_types"] == 0
    assert analysis["reconciles"] is True


def test_reconciliation_false_with_unknown_type():
    rows = [("Goal", "1", "", ""), ("Task", "2", "", "")]
    analysis = _mini_pathway(rows)
    assert analysis["unrecognized_types"] == 1
    assert analysis["reconciles"] is False


def test_reconciliation_false_with_blank_type():
    rows = [("Goal", "1", "", ""), (None, "2", "", "")]
    analysis = _mini_pathway(rows)
    assert analysis["unrecognized_types"] == 1
    assert analysis["reconciles"] is False


def test_type_normalization_handles_case_and_plural():
    rows = [("GOAL", "1", "", ""), ("ACTION ITEMS", "1.1", "", ""),
            ("Action Item", "1.2", "", ""), ("  need ", "1.1.1", "", "")]
    analysis = _mini_pathway(rows)
    assert analysis["type_counts"] == {"Goal": 1, "Action Item": 2, "Need": 1}
    assert analysis["reconciles"] is True


# --------------------------------------------------------------------------- #
# Optional-step: blank is a third state, never folded into "no"/"required".
# --------------------------------------------------------------------------- #

def test_optional_blank_is_unspecified_third_state():
    rows = [("Goal", "1", "", "Yes"), ("Action Items", "1.1", "", "No"),
            ("Need", "1.1.1", "", ""), ("Need", "1.1.2", "", None)]
    analysis = _mini_pathway(rows)
    assert analysis["optional_yes"] == 1
    assert analysis["optional_no"] == 1
    assert analysis["optional_unspecified"] == 2
    assert analysis["optional_yes"] + analysis["optional_no"] + \
        analysis["optional_unspecified"] == analysis["rows"]


def test_optional_states_render_separately(pathway_book):
    export = isn.load_export(pathway_book)
    analysis = isn.analyze_pathway(export["header"], export["rows"])
    report = "\n".join(isn.render_pathway_aggregates(analysis))
    assert "blank-unspecified 6" in report
    assert "treated as required" not in report


# --------------------------------------------------------------------------- #
# Hierarchy integrity (counts only).
# --------------------------------------------------------------------------- #

def test_hierarchy_valid_tree():
    result = isn.analyze_hierarchy([
        ("Goal", "1"), ("Action Item", "1.1"), ("Need", "1.1.1"), ("Need", "1.1.2"),
    ])
    assert result["coded"] == {"Goal": 1, "Action Item": 1, "Need": 2}
    assert result["blank"] == {}
    assert result["malformed"] == {}
    assert result["duplicate_codes"] == 0
    assert result["action_parent_ok"] == 1 and result["action_parent_missing"] == 0
    assert result["need_parent_ok"] == 2 and result["need_parent_missing"] == 0


def test_hierarchy_missing_parents():
    result = isn.analyze_hierarchy([
        ("Action Item", "3.1"),          # no Goal "3"
        ("Need", "1.1.1"),               # no Action Item "1.1"
    ])
    assert result["action_parent_missing"] == 1
    assert result["need_parent_missing"] == 1


def test_hierarchy_duplicate_codes():
    result = isn.analyze_hierarchy([
        ("Goal", "1"), ("Action Item", "1.1"),
        ("Need", "1.1.1"), ("Need", "1.1.1"),
    ])
    assert result["duplicate_codes"] == 1


def test_hierarchy_blank_codes():
    result = isn.analyze_hierarchy([("Goal", None), ("Goal", "  "), ("Action Item", "")])
    assert result["blank"] == {"Goal": 2, "Action Item": 1}
    assert result["coded"] == {}


def test_hierarchy_malformed_codes():
    result = isn.analyze_hierarchy([
        ("Goal", "1.2"),        # wrong depth for a Goal
        ("Action Item", "abc"),  # unparseable
        ("Need", "1.2.3.4"),    # wrong depth for a Need
        ("Need", "1.2.3b"),     # valid: observed letter-suffix shape
    ])
    assert result["malformed"] == {"Goal": 1, "Action Item": 1, "Need": 1}
    assert result["coded"] == {"Need": 1}


def test_hierarchy_letter_suffix_parentage():
    result = isn.analyze_hierarchy([
        ("Goal", "1"), ("Action Item", "1.1"), ("Need", "1.1.2a"),
    ])
    assert result["need_parent_ok"] == 1 and result["need_parent_missing"] == 0


def test_hierarchy_fixture_counts(pathway_book):
    export = isn.load_export(pathway_book)
    analysis = isn.analyze_pathway(export["header"], export["rows"])
    hierarchy = analysis["hierarchy"]
    assert hierarchy["coded"] == {"Goal": 2, "Action Item": 2, "Need": 3}
    assert hierarchy["need_parent_missing"] == 1     # 2.1.1a has no coded parent 2.1
    assert hierarchy["duplicate_codes"] == 0


# --------------------------------------------------------------------------- #
# Cross-workbook join (aggregates only).
# --------------------------------------------------------------------------- #

def test_join_matched_ambiguous_unmatched():
    rows = [
        ("Prog A", PLANTED_ORG, "Cat A", "Svc"),
        ("Prog B", PLANTED_ORG, "Cat A", "Svc"),
        ("Prog B", PLANTED_ORG_2, "Cat B", "Svc"),   # ambiguous title
    ]
    linked = {"prog a", "prog b", "prog zz"}
    join = isn.join_resource_references(MINI_DIRECTORY_HEADER, rows, linked)
    assert join["distinct_references"] == 3
    assert join["matched"] == 1
    assert join["ambiguous"] == 1
    assert join["unmatched"] == 1
    assert join["denominator_rows"] == 3


def test_join_is_deterministic():
    rows = [("Prog A", PLANTED_ORG, "Cat A", "Svc")]
    linked = {"prog a"}
    first = isn.join_resource_references(MINI_DIRECTORY_HEADER, rows, linked)
    second = isn.join_resource_references(MINI_DIRECTORY_HEADER, rows, linked)
    assert first == second


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


def test_parse_code_edges():
    assert isn.parse_code(None) is None
    assert isn.parse_code("") is None
    assert isn.parse_code("abc") is None
    assert isn.parse_code("1.2.3") == ("1", "2", "3")
    assert isn.parse_code("1.2.3b") == ("1", "2", "3")
    assert isn.parse_code(" 1.2 ") == ("1", "2")


def test_classify_header_unknown_and_blank():
    name, category = isn.classify_header("Zzz Mystery", 7)
    assert name == "unclassified-column-7"
    assert category == isn.CAT_TEXT
    name, _ = isn.classify_header(None, 3)
    assert name == "unclassified-column-3"


def test_find_sources_identifies_roles(directory_book, pathway_book, tmp_path):
    roles = isn.find_sources(tmp_path)
    assert roles[isn.ROLE_DIRECTORY].name == "fixture-directory.xlsx"
    assert roles[isn.ROLE_PATHWAY].name == "fixture-pathway.xlsx"


def test_find_sources_requires_exactly_two(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError):
        isn.find_sources(empty)


def test_find_sources_rejects_same_role(tmp_path):
    _write_book(tmp_path / "one.xlsx", [("Data", DIRECTORY_HEADER, DIRECTORY_ROWS, "visible")])
    _write_book(tmp_path / "two.xlsx", [("Data", DIRECTORY_HEADER, DIRECTORY_ROWS, "visible")])
    with pytest.raises(FileNotFoundError, match="same role"):
        isn.find_sources(tmp_path)
