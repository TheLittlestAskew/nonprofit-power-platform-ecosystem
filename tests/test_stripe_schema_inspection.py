"""Unit tests for the sanitized Stripe schema inspector.

All fixtures are INVENTED. No production data is used. These tests exercise
``categorize_field``, ``iter_record_paths``, ``safe_field_report``, and
``load_charge_sample`` from ``scripts/inspect_stripe_schema.py`` and confirm the
inspector reports nested structure while never emitting a value.

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
# Field categorization (leaf-based, dotted paths and [] markers)
# --------------------------------------------------------------------------- #

def test_personal_fields():
    for name in ("billing_details.email", "name", "phone", "address_line1", "tax_id"):
        assert insp.categorize_field(name) == insp.CAT_PERSONAL, name


def test_payment_method_fields():
    for name in ("source.last4", "source.fingerprint", "exp_month", "brand", "cvc_check"):
        assert insp.categorize_field(name) == insp.CAT_PAYMENT, name


def test_identifier_fields():
    for name in ("id", "customer", "payment_intent", "receipt_url"):
        assert insp.categorize_field(name) == insp.CAT_IDENTIFIER, name


def test_financial_fields():
    for name in ("amount", "balance_transaction.fee", "balance_transaction.net", "currency"):
        assert insp.categorize_field(name) == insp.CAT_FINANCIAL, name


def test_pagination_fields():
    for name in ("has_more", "total_count", "starting_after"):
        assert insp.categorize_field(name) == insp.CAT_PAGINATION, name


def test_metadata_fields():
    for name in ("metadata.form_name", "statement_descriptor", "metadata"):
        assert insp.categorize_field(name) == insp.CAT_METADATA, name


def test_unknown_defaults_to_structural():
    for name in ("paid", "captured", "livemode", "disputed"):
        assert insp.categorize_field(name) == insp.CAT_STRUCTURAL, name


def test_list_marker_leaf_is_stripped():
    # refunds.data[] -> leaf 'data' -> structural; refunds.data[].amount -> financial
    assert insp.categorize_field("refunds.data[]") == insp.CAT_STRUCTURAL
    assert insp.categorize_field("refunds.data[].amount") == insp.CAT_FINANCIAL


def test_empty_name_is_structural_not_error():
    assert insp.categorize_field("") == insp.CAT_STRUCTURAL
    assert insp.categorize_field("   ") == insp.CAT_STRUCTURAL


# --------------------------------------------------------------------------- #
# Nested path discovery
# --------------------------------------------------------------------------- #

def _nested_records():
    return [
        {
            "object": "charge",
            "amount": 500,
            "billing_details": {"email": "a@example.invalid", "name": "X"},
            "balance_transaction": {"amount": 500, "fee": 16, "net": 484},
            "metadata": {"form_name": "spring"},
            "source": {"fingerprint": "zzz", "last4": "4242"},
            "refunds": {"object": "list", "data": []},
        },
        {
            "object": "charge",
            "amount": 750,
            "billing_details": {"email": None, "name": "Y"},
            # no balance_transaction on this record
            "metadata": {"form_name": "monthly"},
            "source": {"fingerprint": "yyy", "last4": "1881"},
            "refunds": {"object": "list", "data": []},
        },
    ]


def test_nested_paths_discovered():
    fields = {r["field"] for r in insp.safe_field_report(_nested_records())}
    for path in ("billing_details.email", "balance_transaction.amount",
                 "balance_transaction.fee", "balance_transaction.net",
                 "metadata.form_name", "source.fingerprint"):
        assert path in fields, path
    # container path is distinguished from its children
    assert "billing_details" in fields


def test_nested_sensitive_category():
    report = {r["field"]: r for r in insp.safe_field_report(_nested_records())}
    assert report["source.fingerprint"]["category"] == insp.CAT_PAYMENT
    assert report["billing_details.email"]["category"] == insp.CAT_PERSONAL
    assert report["balance_transaction.amount"]["category"] == insp.CAT_FINANCIAL
    assert report["metadata.form_name"]["category"] == insp.CAT_METADATA


def test_nested_values_never_serialized():
    blob = json.dumps(insp.safe_field_report(_nested_records()))
    for value in ("a@example.invalid", "spring", "monthly", "zzz", "yyy",
                  "4242", "1881", "500", "750", "484"):
        assert value not in blob, value


def test_report_keys_are_structure_only():
    allowed = {"field", "category", "types", "present_pct"}
    for row in insp.safe_field_report(_nested_records()):
        assert set(row.keys()) == allowed
    # No publishable-value flag exists anymore.
    assert not hasattr(insp, "VALUE_PUBLISHABLE")


def test_presence_pct_with_nested_absent():
    report = {r["field"]: r for r in insp.safe_field_report(_nested_records())}
    # balance_transaction present in 1 of 2 records
    assert report["balance_transaction.amount"]["present_pct"] == 50.0
    # billing_details present in both
    assert report["billing_details.name"]["present_pct"] == 100.0


def test_null_and_types_are_captured_without_values():
    report = {r["field"]: r for r in insp.safe_field_report(_nested_records())}
    # email is str in one record, null in the other -> both types, no values
    assert set(report["billing_details.email"]["types"]) == {"null", "str"}


# --------------------------------------------------------------------------- #
# Malformed input safety
# --------------------------------------------------------------------------- #

def test_malformed_list_items_do_not_crash_or_expose():
    records = [
        {"object": "charge", "amount": 1, "refunds": {"data": ["oops-string", 123, None]}},
        "not-a-dict-record",
        None,
        {"object": "charge", "tags": [{"k": "v-secret"}]},
    ]
    report = insp.safe_field_report(records)  # must not raise
    blob = json.dumps(report)
    # scalar list-item VALUES must not leak
    assert "oops-string" not in blob and "v-secret" not in blob and "123" not in blob
    # the list-item path is still discovered (structure), typed only
    fields = {r["field"] for r in report}
    assert "refunds.data[]" in fields
    assert "tags[].k" in fields


def test_iter_record_paths_yields_only_types():
    rec = {"a": 1, "b": {"c": "secret"}, "d": [ "x", {"e": 2} ]}
    pairs = list(insp.iter_record_paths(rec, ""))
    emitted = {p for p, _ in pairs}
    types = {t for _, t in pairs}
    assert "b.c" in emitted and "d[]" in emitted and "d[].e" in emitted
    # only JSON type names are ever emitted as the second element
    assert types <= {"int", "str", "dict", "list", "float", "bool", "null"}


# --------------------------------------------------------------------------- #
# Loading / shape validation
# --------------------------------------------------------------------------- #

def test_safe_field_report_empty():
    assert insp.safe_field_report([]) == []


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
