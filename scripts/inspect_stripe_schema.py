#!/usr/bin/env python3
"""Inspect the surviving Stripe charge sample and emit **sanitized structure only**.

This reads a private Stripe export (a single Stripe ``list`` response of ``charge``
objects) and reports **field-level structure**: field name, privacy category,
observed JSON type, and presence percentage. It **never** prints, logs, or writes
any field *value* — no ids, emails, names, amounts, timestamps, card data, or
metadata values ever leave this script.

Why it exists:
* Grounds the public ``development-finance/data-dictionary.csv`` field taxonomy in
  the real (private) source structure, reproducibly.
* Lets a reviewer confirm the sample is a 74-record charge list without exposing
  any confidential record.

The source lives under ``source-private/`` and is never committed (see
``AGENTS.md`` / ``SECURITY.md``). Run locally with the source present.

Usage:
    python scripts/inspect_stripe_schema.py

Exits non-zero with a clear message if the source is missing or unreadable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = REPO_ROOT / "source-private" / "stripejson.txt"

# --------------------------------------------------------------------------- #
# Privacy categories (the seven buckets from the publication audit).
# A field NAME is Stripe's public API vocabulary and may be documented; whether
# its VALUE may be published is governed by the category below.
# --------------------------------------------------------------------------- #

CAT_STRUCTURAL = "safe-structural"        # publishable (names + enum values)
CAT_FINANCIAL = "financial"               # schema-only (names yes, values no)
CAT_PERSONAL = "personal-contact"         # never publish values
CAT_IDENTIFIER = "processor-identifier"   # never publish values
CAT_PAYMENT = "payment-method-sensitive"  # never publish values
CAT_METADATA = "metadata-freetext"        # never publish values
CAT_PAGINATION = "pagination-api"         # publishable (names + enum values)

# Whether VALUES for a category may appear in public artifacts.
VALUE_PUBLISHABLE = {
    CAT_STRUCTURAL: True,
    CAT_PAGINATION: True,
    CAT_FINANCIAL: False,   # schema-only: names may be documented, values sanitized
    CAT_PERSONAL: False,
    CAT_IDENTIFIER: False,
    CAT_PAYMENT: False,
    CAT_METADATA: False,
}

# Explicit leaf-name sets (case-insensitive). Matching is done on the *leaf*
# segment (after the last ``.``) using exact membership, not loose substring
# tests — so ``paid`` is not mistaken for an id and ``form_name`` is not mistaken
# for a person's name.
_PAYMENT = frozenset({
    "last4", "dynamic_last4", "exp_month", "exp_year", "cvc_check", "brand",
    "funding", "wallet", "tokenization_method", "fingerprint",
    "regulated_status", "allow_redisplay", "card",
})
_METADATA = frozenset({
    "metadata", "description", "statement_descriptor",
    "calculated_statement_descriptor", "statement_descriptor_suffix",
    "form_name", "invoice_id", "advice_code", "network_advice_code",
    "network_decline_code", "seller_message", "reason", "failure_message",
    "failure_code",
})
_PERSONAL = frozenset({"name", "email", "phone", "tax_id", "receipt_email", "shipping"})
_IDENTIFIER = frozenset({
    "id", "customer", "payment_intent", "invoice", "order", "review",
    "transfer_group", "source_transfer", "on_behalf_of", "application",
    "receipt_number", "receipt_url", "destination", "dispute",
})
_PAGINATION = frozenset({"object", "has_more", "starting_after", "total_count", "url"})
_FINANCIAL = frozenset({"amount", "amount_captured", "amount_refunded", "fee", "net",
                        "currency", "exchange_rate", "gross"})


def categorize_field(field_name: str) -> str:
    """Classify a field name into one of the seven privacy categories.

    Name-based only; never inspects values. Matching uses the leaf segment (after
    the last ``.``) against explicit sets, most-sensitive first. Anything with
    ``address`` in the leaf is personal. Unmatched names fall back to
    ``safe-structural`` (booleans/enums such as ``paid``, ``captured``,
    ``status``, ``livemode``). Empty/whitespace names classify as structural
    rather than raising, so a malformed export cannot crash the pass.
    """
    n = (field_name or "").strip().lower()
    if not n:
        return CAT_STRUCTURAL
    leaf = n.split(".")[-1]
    if leaf in _PAYMENT:
        return CAT_PAYMENT
    if leaf in _METADATA:
        return CAT_METADATA
    if "address" in leaf or leaf in _PERSONAL:
        return CAT_PERSONAL
    if leaf in _IDENTIFIER:
        return CAT_IDENTIFIER
    if leaf in _PAGINATION:
        return CAT_PAGINATION
    if leaf in _FINANCIAL or leaf.startswith("amount"):
        return CAT_FINANCIAL
    return CAT_STRUCTURAL


def _json_type(v: object) -> str:
    if isinstance(v, bool):
        return "bool"
    if v is None:
        return "null"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "dict"
    return type(v).__name__


def safe_field_report(records: list[dict]) -> list[dict]:
    """Return sanitized per-field structure for a list of Stripe records.

    Each entry: ``{field, category, types, present_pct, value_publishable}``.
    Only top-level fields are summarized; VALUES are never included.
    """
    n = len(records)
    if n == 0:
        return []
    present: dict[str, int] = {}
    types: dict[str, set] = {}
    for r in records:
        if not isinstance(r, dict):
            continue
        for k, v in r.items():
            present[k] = present.get(k, 0) + 1
            types.setdefault(k, set()).add(_json_type(v))
    out = []
    for field in sorted(present):
        cat = categorize_field(field)
        out.append(
            {
                "field": field,
                "category": cat,
                "types": sorted(types[field]),
                "present_pct": round(100 * present[field] / n, 1),
                "value_publishable": VALUE_PUBLISHABLE[cat],
            }
        )
    return out


def load_charge_sample(source_file: Path) -> list[dict]:
    """Load the ``data[]`` records from a Stripe ``list`` response.

    Raises ``FileNotFoundError`` if absent and ``ValueError`` if the top-level
    shape is not a Stripe list response.
    """
    if not source_file.exists():
        raise FileNotFoundError(
            f"Stripe sample not found: {source_file}\n"
            "This private export lives under source-private/ and is never "
            "committed. Place it there and re-run."
        )
    doc = json.loads(source_file.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(doc, dict) or doc.get("object") != "list" or not isinstance(doc.get("data"), list):
        raise ValueError("source is not a Stripe list response (expected object='list' with data[]).")
    return [r for r in doc["data"] if isinstance(r, dict)]


def main() -> int:
    try:
        records = load_charge_sample(SOURCE_FILE)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1

    # Object-type distribution (record['object']) — type NAMES only, no values.
    obj_types: dict[str, int] = {}
    for r in records:
        obj_types[r.get("object", "?")] = obj_types.get(r.get("object", "?"), 0) + 1

    report = safe_field_report(records)
    cat_counts: dict[str, int] = {}
    for row in report:
        cat_counts[row["category"]] = cat_counts.get(row["category"], 0) + 1

    print(f"Stripe sample: {len(records)} record(s); object types: {obj_types}")
    print(f"Top-level fields: {len(report)}")
    print("Fields by privacy category (names only):")
    for cat in sorted(cat_counts):
        print(f"  {cat:24} {cat_counts[cat]:>3}  values_publishable={VALUE_PUBLISHABLE[cat]}")
    print("\nField structure (NO VALUES):")
    print(f"  {'field':26} {'category':24} {'present%':>8}  types")
    for row in report:
        print(f"  {row['field']:26} {row['category']:24} {row['present_pct']:7.1f}%  {row['types']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
