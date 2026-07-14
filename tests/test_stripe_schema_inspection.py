"""Unit tests for the sanitized Stripe schema inspector.

All fixtures are INVENTED. No production data is used. These tests exercise
``categorize_field``, ``safe_field_report``, and ``load_charge_sample`` from
``scripts/inspect_stripe_schema.py`` and confirm the inspector never emits values.

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import inspect_stripe_schema as insp  # noqa: E402


# --------------------------------------------------------------------------- #
# Field categorization
# --------------------------------------------------------------------------- #

def test_personal_fields():
    for name in ("billing_details.email", "name", "phone", "address_line1", "tax_id"):
        assert insp.categorize_field(name) == insp.CAT_PERSONAL, name


def test_payment_method_fields():
    for name in ("last4", "fingerprint", "exp_month", "brand", "cvc_check"):
        assert insp.categorize_field(name) == insp.CAT_PAYMENT, name


def test_identifier_fields():
    for name in ("id", "customer", "payment_intent", "receipt_url"):
        assert insp.categorize_field(name) == insp.CAT_IDENTIFIER, name


def test_financial_fields():
    for name in ("amount", "fee", "net", "currency"):
        assert insp.categorize_field(name) == insp.CAT_FINANCIAL, name


def test_pagination_fields():
    for name in ("has_more", "total_count", "starting_after"):
        assert insp.categorize_field(name) == insp.CAT_PAGINATION, name


def test_metadata_fields():
    for name in ("metadata", "statement_descriptor", "form_name"):
        assert insp.categorize_field(name) == insp.CAT_METADATA, name


def test_unknown_defaults_to_structural():
    for name in ("paid", "captured", "livemode", "disputed"):
        assert insp.categorize_field(name) == insp.CAT_STRUCTURAL, name


def test_empty_name_is_structural_not_error():
    assert insp.categorize_field("") == insp.CAT_STRUCTURAL
    assert insp.categorize_field("   ") == insp.CAT_STRUCTURAL


def test_sensitive_categories_are_not_value_publishable():
    for cat in (insp.CAT_PERSONAL, insp.CAT_IDENTIFIER, insp.CAT_PAYMENT, insp.CAT_METADATA, insp.CAT_FINANCIAL):
        assert insp.VALUE_PUBLISHABLE[cat] is False
    for cat in (insp.CAT_STRUCTURAL, insp.CAT_PAGINATION):
        assert insp.VALUE_PUBLISHABLE[cat] is True


# --------------------------------------------------------------------------- #
# Safe report (no values)
# --------------------------------------------------------------------------- #

def _invented_records():
    return [
        {"object": "charge", "amount": 500, "paid": True,
         "billing_details": {"email": "a@example.test"}, "id": "SAMPLE-CHG-1"},
        {"object": "charge", "amount": 750, "paid": True,
         "billing_details": {"email": None}, "id": "SAMPLE-CHG-2"},
    ]


def test_safe_field_report_has_no_values():
    report = insp.safe_field_report(_invented_records())
    # The report must contain only field/category/type/presence metadata.
    allowed = {"field", "category", "types", "present_pct", "value_publishable"}
    for row in report:
        assert set(row.keys()) == allowed
    # No invented value should appear anywhere in the serialized report.
    blob = json.dumps(report)
    assert "500" not in blob and "750" not in blob
    assert "example.test" not in blob and "SAMPLE-CHG-1" not in blob


def test_safe_field_report_presence_and_category():
    report = {r["field"]: r for r in insp.safe_field_report(_invented_records())}
    assert report["amount"]["present_pct"] == 100.0
    assert report["amount"]["category"] == insp.CAT_FINANCIAL
    assert report["id"]["category"] == insp.CAT_IDENTIFIER
    assert report["id"]["value_publishable"] is False


def test_safe_field_report_empty():
    assert insp.safe_field_report([]) == []


# --------------------------------------------------------------------------- #
# Loading / shape validation
# --------------------------------------------------------------------------- #

def test_load_missing_raises(tmp_path):
    try:
        insp.load_charge_sample(tmp_path / "nope.json")
    except FileNotFoundError as exc:
        assert "source-private" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected FileNotFoundError")


def test_load_rejects_non_list_response(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"object": "charge", "id": "x"}), encoding="utf-8")
    try:
        insp.load_charge_sample(p)
    except ValueError as exc:
        assert "list response" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for non-list response")


def test_load_accepts_list_response(tmp_path):
    p = tmp_path / "ok.json"
    p.write_text(json.dumps({"object": "list", "has_more": False,
                             "data": [{"object": "charge", "amount": 1}]}), encoding="utf-8")
    recs = insp.load_charge_sample(p)
    assert len(recs) == 1 and recs[0]["object"] == "charge"
