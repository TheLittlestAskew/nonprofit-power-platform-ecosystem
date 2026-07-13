"""Unit tests for the Dataverse inventory classification and prefix logic.

All fixtures here are INVENTED. No production data is used. These tests exercise
``has_custom_prefix``, ``classify_custom_table``, ``TableRow.is_custom``, and
``build_catalog`` from ``scripts/build_dataverse_inventory.py``.

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import json
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


def test_intersect_by_embedded_managed_entity():
    # A tr_-published join onto managed msnfp_ entities is an intersect, even
    # though it contains no bare '_tr_' pattern and carries an 'N/A' description.
    classification, basis = inv.classify_custom_table("tr_msnfp_award_msnfp_indicator", "N/A")
    assert classification == inv.CLASS_INTERSECT
    assert "intersect" in basis.lower()


def test_intersect_by_embedded_cdm_entity():
    classification, _ = inv.classify_custom_table("tr_msnfp_deliveryframework_cdm_company", "N/A")
    assert classification == inv.CLASS_INTERSECT


def test_intersect_structure_helper():
    assert inv.is_intersect_by_structure("tr_volunteer_msnfp_participation") is True
    assert inv.is_intersect_by_structure("tr_guest") is False
    # The entity's own leading prefix must not be mistaken for a second entity.
    assert inv.is_intersect_by_structure("tr_msnfp_award") is False


def test_na_description_is_not_usable():
    assert inv.has_usable_description("N/A") is False
    assert inv.has_usable_description("n/a") is False
    assert inv.has_usable_description("") is False
    assert inv.has_usable_description("Records of guest budgets") is True


def test_na_description_single_entity_is_unclear():
    # A lone entity whose only description is 'N/A' cannot be verified.
    classification, _ = inv.classify_custom_table("tr_actionitem", "N/A")
    assert classification == inv.CLASS_UNCLEAR


def test_support_token_log():
    classification, basis = inv.classify_custom_table("tr_activitylog", "activity log")
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


# --------------------------------------------------------------------------- #
# Sensitive-name generalization
#
# NOTE: These fixtures are INVENTED. The real private schema-name -> public-label
# mapping is never stored in this tracked test file; it lives only in the
# git-ignored source-private/sensitive-generalizations.json config. Here we test
# the *behavior* of public_display / load_sensitive_generalizations against
# invented inputs, so no production identifier appears in version control.
# --------------------------------------------------------------------------- #

# Invented mapping used to exercise the generalization behavior.
FIXTURE_MAP = {
    "tr_sensitive_assessment_a": "Behavioral-health assessment",
    "tr_sensitive_assessment_b": "Behavioral-health assessment",
    "tr_sensitive_classification_a": "Clinical classification",
    "tr_sensitive_treatment_a": "Counseling treatment goals",
}


def test_sensitive_schema_is_generalized():
    label, generalized = inv.public_display("tr_sensitive_assessment_a", FIXTURE_MAP)
    assert generalized is True
    assert label == "Behavioral-health assessment"
    # the exact (invented) identifier is not echoed back in the label
    assert "sensitive" not in label.lower()


def test_sensitive_generalization_is_case_insensitive():
    label, generalized = inv.public_display("TR_SENSITIVE_CLASSIFICATION_A", FIXTURE_MAP)
    assert generalized is True
    assert label == "Clinical classification"


def test_ordinary_schema_is_not_generalized():
    label, generalized = inv.public_display("tr_guest", FIXTURE_MAP)
    assert generalized is False
    assert label == "tr_guest"


def test_two_structures_share_one_public_domain():
    # Two distinct sensitive tables can generalize to the same public domain.
    assert inv.public_display("tr_sensitive_assessment_a", FIXTURE_MAP)[0] == "Behavioral-health assessment"
    assert inv.public_display("tr_sensitive_assessment_b", FIXTURE_MAP)[0] == "Behavioral-health assessment"


# --------------------------------------------------------------------------- #
# Runtime loading of the ignored sensitive-generalization config
# --------------------------------------------------------------------------- #

def _write_config(tmp_path, payload):
    p = tmp_path / "sensitive-generalizations.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_load_config_returns_lowercased_map(tmp_path):
    cfg = _write_config(tmp_path, {"generalizations": {"TR_Sensitive_Assessment_A": "Behavioral-health assessment"}})
    mapping = inv.load_sensitive_generalizations(cfg)
    assert mapping == {"tr_sensitive_assessment_a": "Behavioral-health assessment"}


def test_load_config_missing_raises_filenotfound(tmp_path):
    missing = tmp_path / "does-not-exist.json"
    try:
        inv.load_sensitive_generalizations(missing)
    except FileNotFoundError as exc:
        assert "source-private" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected FileNotFoundError for missing config")


def test_load_config_bad_structure_raises_valueerror(tmp_path):
    cfg = _write_config(tmp_path, {"not_generalizations": {}})
    try:
        inv.load_sensitive_generalizations(cfg)
    except ValueError as exc:
        assert "generalizations" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for missing 'generalizations' key")


def test_load_config_empty_mapping_raises_valueerror(tmp_path):
    cfg = _write_config(tmp_path, {"generalizations": {}})
    try:
        inv.load_sensitive_generalizations(cfg)
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for empty mapping")


def test_load_config_error_does_not_leak_key(tmp_path):
    # An invalid (empty) label must raise WITHOUT echoing the private key.
    cfg = _write_config(tmp_path, {"generalizations": {"tr_secret_identifier": ""}})
    try:
        inv.load_sensitive_generalizations(cfg)
    except ValueError as exc:
        assert "tr_secret_identifier" not in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for empty label")
