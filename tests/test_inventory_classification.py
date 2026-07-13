"""Unit tests for the Dataverse inventory classification and prefix logic.

All fixtures here are INVENTED. No production data is used. These tests exercise
``has_custom_prefix``, ``classify_custom_table``, ``TableRow.is_custom``, and
``build_catalog`` from ``scripts/build_dataverse_inventory.py``.

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the scripts/ directory importable without installing a package.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_dataverse_inventory as inv  # noqa: E402


# --------------------------------------------------------------------------- #
# Prefix detection
# --------------------------------------------------------------------------- #

def test_prefix_detected_on_schema_name():
    assert inv.has_custom_prefix("tr_widget", "tr_widget") is True


def test_prefix_detected_when_only_logical_name_has_it():
    assert inv.has_custom_prefix("", "tr_widget") is True


def test_prefix_is_case_insensitive_and_trimmed():
    assert inv.has_custom_prefix("  TR_Widget ", "") is True


def test_other_publisher_prefix_is_not_custom():
    # Contains 'tr_' but starts with a different publisher prefix -> excluded.
    assert inv.has_custom_prefix("cr57f_tr_budget_details", "cr57f_tr_budget_details") is False


def test_standard_table_is_not_custom():
    assert inv.has_custom_prefix("account", "account") is False


def test_empty_names_are_not_custom():
    assert inv.has_custom_prefix("", "") is False


def test_tablerow_is_custom_matches_helper():
    row = inv.TableRow("Widget", "A widget", "tr_widget", "tr_widget")
    assert row.is_custom() is True
    std = inv.TableRow("Account", "Std", "account", "account")
    assert std.is_custom() is False


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #

def test_intersect_pattern_double_prefix():
    classification, basis = inv.classify_custom_table("tr_attendee_tr_volunteer", "links attendees and volunteers")
    assert classification == inv.CLASS_INTERSECT
    assert "_tr_" in basis or "intersect" in basis.lower()


def test_intersect_wins_even_with_description():
    # An intersect-named row is classified as intersect regardless of description.
    classification, _ = inv.classify_custom_table("tr_bills_tr_locations", "a description")
    assert classification == inv.CLASS_INTERSECT


def test_support_token_log():
    classification, basis = inv.classify_custom_table("tr_medlog", "medication log")
    assert classification == inv.CLASS_SUPPORT
    assert "log" in basis


def test_support_token_mapping():
    classification, _ = inv.classify_custom_table("tr_vendormapping", "maps vendors")
    assert classification == inv.CLASS_SUPPORT


def test_core_business_with_description():
    classification, _ = inv.classify_custom_table("tr_guest", "a guest staying at the shelter")
    assert classification == inv.CLASS_CORE


def test_underscore_alone_is_not_intersect():
    # A single underscore / relational-looking name without the _tr_ pattern
    # must NOT be classified as an intersect table.
    classification, _ = inv.classify_custom_table("tr_case_meeting", "a case meeting")
    assert classification == inv.CLASS_CORE


def test_no_description_is_unclear():
    classification, basis = inv.classify_custom_table("tr_mystery", "")
    assert classification == inv.CLASS_UNCLEAR
    assert "manual review" in basis or "no description" in basis


# --------------------------------------------------------------------------- #
# Catalog assembly
# --------------------------------------------------------------------------- #

def test_build_catalog_filters_and_sorts():
    rows = [
        inv.TableRow("Account", "Std MS table", "account", "account"),          # excluded
        inv.TableRow("Zeta", "custom biz", "tr_zeta", "tr_zeta"),               # included
        inv.TableRow("Alpha", "custom biz", "tr_alpha", "tr_alpha"),           # included
        inv.TableRow("Budget", "other publisher", "cr57f_tr_budget", "cr57f_tr_budget"),  # excluded
        inv.TableRow("Link", "n:n", "tr_a_tr_b", "tr_a_tr_b"),                 # included, intersect
    ]
    catalog = inv.build_catalog(rows)
    schemas = [c.table.schema_name for c in catalog]
    # Only tr_ tables, sorted alphabetically by schema name.
    assert schemas == ["tr_a_tr_b", "tr_alpha", "tr_zeta"]
    # The intersect row is classified as intersect.
    by_schema = {c.table.schema_name: c.classification for c in catalog}
    assert by_schema["tr_a_tr_b"] == inv.CLASS_INTERSECT
    assert by_schema["tr_alpha"] == inv.CLASS_CORE


def test_counts_cover_all_four_buckets():
    rows = [
        inv.TableRow("Biz", "desc", "tr_biz", "tr_biz"),
        inv.TableRow("Log", "audit log", "tr_thing_log", "tr_thing_log"),
        inv.TableRow("Link", "n:n", "tr_a_tr_b", "tr_a_tr_b"),
        inv.TableRow("Mystery", "", "tr_mystery", "tr_mystery"),
    ]
    catalog = inv.build_catalog(rows)
    counts = inv._counts(catalog)
    assert counts[inv.CLASS_CORE] == 1
    assert counts[inv.CLASS_SUPPORT] == 1
    assert counts[inv.CLASS_INTERSECT] == 1
    assert counts[inv.CLASS_UNCLEAR] == 1


# --------------------------------------------------------------------------- #
# Required-column validation
# --------------------------------------------------------------------------- #

def test_resolve_columns_maps_case_insensitively():
    header = ("entity", "DESCRIPTION", "Schema Name", "logical name")
    cols = inv._resolve_columns(header)
    assert cols["Entity"] == 0
    assert cols["Description"] == 1
    assert cols["Schema Name"] == 2
    assert cols["Logical Name"] == 3


def test_resolve_columns_raises_on_missing():
    header = ("Entity", "Description")  # missing schema/logical
    try:
        inv._resolve_columns(header)
    except KeyError as exc:
        assert "Schema Name" in str(exc) and "Logical Name" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected KeyError for missing required columns")
