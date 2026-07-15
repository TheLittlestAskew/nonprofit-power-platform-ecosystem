"""Unit tests for the development-finance sample validator.

All fixtures are INVENTED. These exercise ``scan_for_real_identifiers`` and
``validate_samples`` from ``scripts/validate_finance_samples.py`` and also assert
that the committed ``development-finance/sample-records.json`` passes.

The email fixtures use RFC 6761 reserved domains (``example.invalid`` is the only
accepted one; ``example.com`` and real domains must be rejected).

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_finance_samples as vfs  # noqa: E402


def _good_doc():
    scenarios = [
        {"id": f"SAMPLE-SCN-{i:02d}", "scenario": name}
        for i, name in enumerate(sorted(vfs._REQUIRED_SCENARIOS), start=1)
    ]
    # the reconciled scenario needs a status
    for s in scenarios:
        if s["scenario"] == "reconciled_relationship":
            s["reconciliation_status"] = "reconciled"
    return {
        "sample_data": True,
        "deposits": [{"id": "SAMPLE-DEP-001", "net_total": 1209}],
        "transactions": [{"id": "SAMPLE-CHG-001", "deposit_reference": "SAMPLE-DEP-001"}],
        "scenarios": scenarios,
    }


# --------------------------------------------------------------------------- #
# Email domain policy
# --------------------------------------------------------------------------- #

def test_example_invalid_accepted():
    assert vfs.scan_for_real_identifiers({"e": "sample.donor@example.invalid"}) == []


def test_example_com_rejected():
    problems = vfs.scan_for_real_identifiers({"e": "sample.donor@example.com"})
    assert any("email domain" in p for p in problems)


def test_real_looking_domain_rejected():
    problems = vfs.scan_for_real_identifiers({"e": "donor@gmail.com"})
    assert any("email domain" in p for p in problems)


def test_subdomain_of_example_invalid_rejected():
    # domain must be exactly example.invalid, not a subdomain
    problems = vfs.scan_for_real_identifiers({"e": "x@mail.example.invalid"})
    assert any("email domain" in p for p in problems)


# --------------------------------------------------------------------------- #
# Other real-identifier scanning
# --------------------------------------------------------------------------- #

def test_flags_real_stripe_id():
    problems = vfs.scan_for_real_identifiers({"x": "ch_3PabcdEFGH12345"})
    assert any("Stripe id" in p for p in problems)


def test_flags_guid():
    problems = vfs.scan_for_real_identifiers({"x": "12345678-1234-1234-1234-123456789abc"})
    assert any("GUID" in p for p in problems)


def test_flags_card_like_digits():
    problems = vfs.scan_for_real_identifiers({"x": "4111 1111 1111 1111"})
    assert any("card-like" in p for p in problems)


def test_clean_sample_has_no_identifier_problems():
    assert vfs.scan_for_real_identifiers(_good_doc()) == []


# --------------------------------------------------------------------------- #
# Structural validation
# --------------------------------------------------------------------------- #

def test_good_doc_validates():
    assert vfs.validate_samples(_good_doc()) == []


def test_missing_sample_flag_fails():
    doc = _good_doc()
    doc["sample_data"] = False
    assert any("sample_data" in p for p in vfs.validate_samples(doc))


def test_missing_section_fails():
    doc = _good_doc()
    del doc["deposits"]
    assert any("deposits" in p for p in vfs.validate_samples(doc))


def test_id_without_fiction_marker_fails():
    doc = _good_doc()
    doc["deposits"][0]["id"] = "DEP-001"
    assert any("fiction marker" in p for p in vfs.validate_samples(doc))


def test_missing_lower_confidence_scenario_fails():
    doc = _good_doc()
    doc["scenarios"] = [s for s in doc["scenarios"] if s["scenario"] != "lower_confidence_review"]
    assert any("lower_confidence_review" in p for p in vfs.validate_samples(doc))


def test_missing_duplicate_prevention_scenario_fails():
    doc = _good_doc()
    doc["scenarios"] = [s for s in doc["scenarios"] if s["scenario"] != "duplicate_detected"]
    assert any("duplicate_detected" in p for p in vfs.validate_samples(doc))


def test_missing_reconciliation_status_fails():
    doc = _good_doc()
    for s in doc["scenarios"]:
        if s["scenario"] == "reconciled_relationship":
            s.pop("reconciliation_status", None)
    assert any("reconciliation_status" in p for p in vfs.validate_samples(doc))


def test_embedded_bad_email_domain_in_sample_fails():
    doc = _good_doc()
    doc["transactions"][0]["donor_display"] = "real.person@example.com"
    assert any("email domain" in p for p in vfs.validate_samples(doc))


# --------------------------------------------------------------------------- #
# The committed sample file must pass
# --------------------------------------------------------------------------- #

def test_committed_sample_file_is_valid():
    doc = json.loads(vfs.SAMPLE_FILE.read_text(encoding="utf-8"))
    assert vfs.validate_samples(doc) == []
