"""Unit tests for the development-finance sample validator.

All fixtures are INVENTED. These exercise ``scan_for_real_identifiers`` and
``validate_samples`` from ``scripts/validate_finance_samples.py`` and also assert
that the committed ``development-finance/sample-records.json`` passes.

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
    return {
        "sample_data": True,
        "deposits": [{"id": "SAMPLE-DEP-001", "net_total": 1209}],
        "transactions": [{"id": "SAMPLE-CHG-001", "deposit_reference": "SAMPLE-DEP-001"}],
        "donor_match_examples": [{"id": "SAMPLE-MATCH-001", "match_signal": "existing processor-customer relationship"}],
        "exception_examples": [{"id": "SAMPLE-EXC-001", "reason": "no matching donor found"}],
    }


# --------------------------------------------------------------------------- #
# Real-identifier scanning (negative safety check)
# --------------------------------------------------------------------------- #

def test_flags_real_stripe_id():
    problems = vfs.scan_for_real_identifiers({"x": "ch_3PabcdEFGH12345"})
    assert any("Stripe id" in p for p in problems)


def test_flags_email():
    problems = vfs.scan_for_real_identifiers({"x": "donor@example.com"})
    assert any("email" in p for p in problems)


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
    problems = vfs.validate_samples(doc)
    assert any("sample_data" in p for p in problems)


def test_missing_section_fails():
    doc = _good_doc()
    del doc["exception_examples"]
    problems = vfs.validate_samples(doc)
    assert any("exception_examples" in p for p in problems)


def test_id_without_fiction_marker_fails():
    doc = _good_doc()
    doc["deposits"][0]["id"] = "DEP-001"  # no SAMPLE/FICTIONAL marker
    problems = vfs.validate_samples(doc)
    assert any("fiction marker" in p for p in problems)


def test_match_example_missing_signal_fails():
    doc = _good_doc()
    del doc["donor_match_examples"][0]["match_signal"]
    problems = vfs.validate_samples(doc)
    assert any("match_signal" in p for p in problems)


def test_embedded_email_in_sample_fails():
    doc = _good_doc()
    doc["transactions"][0]["donor_display"] = "real.person@example.com"
    problems = vfs.validate_samples(doc)
    assert any("email" in p for p in problems)


# --------------------------------------------------------------------------- #
# The committed sample file must pass
# --------------------------------------------------------------------------- #

def test_committed_sample_file_is_valid():
    doc = json.loads(vfs.SAMPLE_FILE.read_text(encoding="utf-8"))
    assert vfs.validate_samples(doc) == []
