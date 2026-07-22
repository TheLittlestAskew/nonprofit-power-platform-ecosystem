"""Unit tests for the service-navigation module validator.

All fixtures are INVENTED. These exercise ``scan_text``, ``validate_samples``,
``validate_dictionary``, and ``check_markdown`` from
``scripts/validate_service_navigation_samples.py``, and assert that the
committed public module files pass every check.

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_service_navigation_samples as vsn  # noqa: E402


@pytest.fixture()
def good_doc():
    return json.loads(vsn.SAMPLE_FILE.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# The committed module must be fully valid.
# --------------------------------------------------------------------------- #

def test_committed_samples_pass(good_doc):
    assert vsn.validate_samples(good_doc) == []


def test_committed_dictionary_passes():
    text = vsn.DICTIONARY_FILE.read_text(encoding="utf-8")
    assert vsn.validate_dictionary(text) == []


def test_whole_module_passes():
    assert vsn.validate_module() == []


# --------------------------------------------------------------------------- #
# Leakage scanning.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("bad,label", [
    ("id 12345678-1234-1234-1234-123456789abc", "GUID"),
    ("QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVphYmNkZWZnaGlqa2xt", "checksum"),
    ("write to person@example.com", "email domain"),
    ("call 555-123-4567 today", "phone"),
    ("digits 12345678901", "phone"),
    ("see https://real-site.org/page", "URL host"),
    ("column tr_sample", "schema prefix"),
    ("column msnfp_sample", "schema prefix"),
    ("visit 123 Fixture Street today", "street-address"),
])
def test_scan_text_flags_leakage(bad, label):
    assert vsn.scan_text(bad, "fixture"), f"expected a problem for {label}"


def test_scan_text_allows_safe_text():
    safe = ("204 resource rows, 199 distinct organizations. "
            "contact@example.invalid and https://example.invalid/resource are reserved. "
            "Recomputed 2026-07-15.")
    assert vsn.scan_text(safe, "fixture") == []


# --------------------------------------------------------------------------- #
# Sample-document structure: each requirement is individually enforced.
# --------------------------------------------------------------------------- #

def _steps(doc):
    return doc["pathway_templates"][0]["steps"]


def test_missing_sample_flag_flagged(good_doc):
    good_doc["sample_data"] = False
    assert any("sample_data" in p for p in vsn.validate_samples(good_doc))


def test_multi_program_org_required(good_doc):
    for resource in good_doc["resources"]:
        resource["organization_title"] = f"Org {resource['id']}"
    assert any("multiple programs" in p for p in vsn.validate_samples(good_doc))


def test_multi_category_resource_required(good_doc):
    for resource in good_doc["resources"]:
        resource["top_level_categories"] = resource["top_level_categories"][:1]
    assert any("multi-category" in p for p in vsn.validate_samples(good_doc))


def test_optional_step_required(good_doc):
    for step in _steps(good_doc):
        if step["optional_step"]:
            step["optional_step"] = False
    assert any("optional step" in p for p in vsn.validate_samples(good_doc))


def test_multiple_action_items_required(good_doc):
    doc = copy.deepcopy(good_doc)
    steps = _steps(doc)
    keep = {"SAMPLE-GOAL-001", "SAMPLE-ACTION-001", "SAMPLE-NEED-001", "SAMPLE-NEED-002"}
    doc["pathway_templates"][0]["steps"] = [s for s in steps if s["id"] in keep]
    doc["individual_plans"] = [
        {
            "plan_reference": "SAMPLE-PLAN-002",
            "copied_from_pathway": "SAMPLE-PATH-001",
            "steps": [{
                "id": "SAMPLE-PLAN-STEP-101", "copied_from": "SAMPLE-GOAL-001",
                "step_code": "1", "step_type": "Goal", "parent": None,
                "plan_status": "in progress",
            }],
        }
    ]
    assert any("multiple Action Items" in p for p in vsn.validate_samples(doc))


def test_action_item_with_multiple_needs_required(good_doc):
    steps = [s for s in _steps(good_doc) if s["id"] != "SAMPLE-NEED-002"]
    good_doc["pathway_templates"][0]["steps"] = steps
    good_doc["individual_plans"][0]["steps"] = [
        s for s in good_doc["individual_plans"][0]["steps"]
        if s["copied_from"] != "SAMPLE-NEED-002"
    ]
    assert any("multiple Needs" in p for p in vsn.validate_samples(good_doc))


def test_resource_linkage_required(good_doc):
    good_doc["pathway_templates"][0]["linked_resource"] = "SAMPLE-RESOURCE-MISSING"
    assert any("links to a sample resource" in p for p in vsn.validate_samples(good_doc))


# --------------------------------------------------------------------------- #
# Hierarchy integrity.
# --------------------------------------------------------------------------- #

def test_missing_parent_flagged(good_doc):
    for step in _steps(good_doc):
        if step["id"] == "SAMPLE-NEED-001":
            step["parent"] = "SAMPLE-ACTION-MISSING"
    assert any("not found" in p for p in vsn.validate_samples(good_doc))


def test_wrong_parent_type_flagged(good_doc):
    for step in _steps(good_doc):
        if step["id"] == "SAMPLE-NEED-001":
            step["parent"] = "SAMPLE-GOAL-001"
    assert any("parent type" in p for p in vsn.validate_samples(good_doc))


def test_wrong_code_depth_flagged(good_doc):
    for step in _steps(good_doc):
        if step["id"] == "SAMPLE-ACTION-001":
            step["step_code"] = "1.1.9"
    problems = vsn.validate_samples(good_doc)
    assert any("depth" in p for p in problems)


def test_code_must_extend_parent_flagged(good_doc):
    for step in _steps(good_doc):
        if step["id"] == "SAMPLE-NEED-001":
            step["step_code"] = "9.9.1"
    assert any("extend the parent" in p for p in vsn.validate_samples(good_doc))


def test_goal_with_parent_flagged(good_doc):
    for step in _steps(good_doc):
        if step["step_type"] == "Goal":
            step["parent"] = "SAMPLE-ACTION-001"
    assert any("Goal must have parent null" in p for p in vsn.validate_samples(good_doc))


def test_nonboolean_optional_flagged(good_doc):
    for step in _steps(good_doc):
        if step["id"] == "SAMPLE-NEED-003":
            del step["optional_step"]
    assert any("explicit boolean" in p for p in vsn.validate_samples(good_doc))


def test_unmarked_id_flagged(good_doc):
    _steps(good_doc)[0]["id"] = "GOAL-1"
    assert any("fiction marker" in p for p in vsn.validate_samples(good_doc))


# --------------------------------------------------------------------------- #
# Individualized-plan copies.
# --------------------------------------------------------------------------- #

def test_broken_copied_from_flagged(good_doc):
    good_doc["individual_plans"][0]["steps"][0]["copied_from"] = "SAMPLE-GONE-001"
    assert any("copied_from" in p for p in vsn.validate_samples(good_doc))


def test_invalid_plan_status_flagged(good_doc):
    good_doc["individual_plans"][0]["steps"][0]["plan_status"] = "done-ish"
    assert any("plan_status" in p for p in vsn.validate_samples(good_doc))


def test_plan_parent_must_be_plan_step(good_doc):
    good_doc["individual_plans"][0]["steps"][1]["parent"] = "SAMPLE-GOAL-001"
    assert any("copied plan step" in p for p in vsn.validate_samples(good_doc))


def test_leaky_sample_value_flagged(good_doc):
    good_doc["resources"][0]["summary"] = "email person@real-domain.org"
    assert any("email domain" in p for p in vsn.validate_samples(good_doc))


# --------------------------------------------------------------------------- #
# Data dictionary.
# --------------------------------------------------------------------------- #

def _dictionary_rows():
    return vsn.DICTIONARY_FILE.read_text(encoding="utf-8").splitlines()


def test_dictionary_bad_treatment_flagged():
    lines = _dictionary_rows()
    lines[1] = lines[1].replace("Never publish", "Publish freely")
    problems = vsn.validate_dictionary("\n".join(lines))
    assert any("approved label set" in p for p in problems)


def test_dictionary_wrong_header_flagged():
    lines = _dictionary_rows()
    lines[0] = lines[0].replace("Public Field", "Field")
    problems = vsn.validate_dictionary("\n".join(lines))
    assert any("expected columns" in p for p in problems)


def test_dictionary_wrong_column_count_flagged():
    lines = _dictionary_rows()
    lines.append("only,three,cells")
    problems = vsn.validate_dictionary("\n".join(lines))
    assert any("wrong column count" in p for p in problems)


def test_dictionary_empty_flagged():
    assert vsn.validate_dictionary("") == ["data dictionary is empty"]


# --------------------------------------------------------------------------- #
# Markdown link + Mermaid checks.
# --------------------------------------------------------------------------- #

def test_broken_relative_link_flagged(tmp_path):
    page = tmp_path / "page.md"
    page.write_text("see [gone](missing-file.md)", encoding="utf-8")
    problems = vsn.check_markdown(page, page.read_text(encoding="utf-8"))
    assert any("broken relative link" in p for p in problems)


def test_resolving_link_and_valid_mermaid_pass(tmp_path):
    (tmp_path / "target.md").write_text("x", encoding="utf-8")
    page = tmp_path / "page.md"
    page.write_text(
        "see [ok](target.md)\n\n```mermaid\nflowchart TD\n  A --> B\n```\n",
        encoding="utf-8",
    )
    assert vsn.check_markdown(page, page.read_text(encoding="utf-8")) == []


def test_unknown_mermaid_type_flagged(tmp_path):
    page = tmp_path / "page.md"
    page.write_text("```mermaid\nnot-a-diagram\n```\n", encoding="utf-8")
    problems = vsn.check_markdown(page, page.read_text(encoding="utf-8"))
    assert any("diagram type" in p for p in problems)
