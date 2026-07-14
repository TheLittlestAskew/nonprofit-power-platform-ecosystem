#!/usr/bin/env python3
"""Inspect the surviving Stripe charge sample and emit **sanitized structure only**.

This reads a private Stripe export (a single Stripe ``list`` response of ``charge``
objects) and reports **field-level structure**: dotted field path, privacy
category, observed JSON type(s), and presence percentage — plus aggregate record
and object-type counts.

**No production record value is ever published.** Only sanitized structure and
aggregate characteristics are reported. The inspector never prints, logs, writes,
or serializes any field value — no booleans, enum values, statuses, timestamps,
dates, currencies, URLs, identifiers, amounts, metadata, contact data, or card
data. An allowlisted *aggregate* statement such as "74 charge objects" is
permitted; that is not a record-level value.

The source lives under ``source-private/`` and is never committed (see
``AGENTS.md`` / ``SECURITY.md``). Run locally with the source present.

Usage:
    python scripts/inspect_stripe_schema.py

Exits non-zero with a clear message if the source is missing or unreadable.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = REPO_ROOT / "source-private" / "stripejson.txt"

# --------------------------------------------------------------------------- #
# Privacy categories (the seven buckets from the publication audit).
#
# A field NAME is Stripe's public API vocabulary and may be documented. A field
# VALUE is NEVER publishable, in any category — the inspector reports structure
# and aggregate characteristics only. The category communicates *how sensitive*
# the withheld values are, not whether any value may be shown.
# --------------------------------------------------------------------------- #

CAT_STRUCTURAL = "safe-structural"        # names + aggregate structure only
CAT_FINANCIAL = "financial"               # names only; values never published
CAT_PERSONAL = "personal-contact"         # names only; values never published
CAT_IDENTIFIER = "processor-identifier"   # names only; values never published
CAT_PAYMENT = "payment-method-sensitive"  # names only; values never published
CAT_METADATA = "metadata-freetext"        # names only; values never published
CAT_PAGINATION = "pagination-api"         # names + aggregate structure only

# What this inspector is permitted to publish. Field VALUES appear nowhere here.
PUBLISHABLE_ELEMENTS = (
    "field paths",
    "privacy categories",
    "observed JSON types",
    "field-presence percentages",
    "aggregate record counts",
    "aggregate object-type names/counts",
    "pagination field structure",
)

# Explicit leaf-name sets (case-insensitive). Matching is on the *leaf* segment
# (after the last ``.`` and without a trailing ``[]``) using exact membership,
# not loose substring tests — so ``paid`` is not mistaken for an id and
# ``form_name`` is not mistaken for a person's name.
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
    """Classify a field path into one of the seven privacy categories.

    Name-based only; never inspects values. Matching uses the leaf segment (after
    the last ``.``, with any trailing ``[]`` list marker removed) against explicit
    sets, most-sensitive first. Anything with ``address`` in the leaf is personal.
    Unmatched names fall back to ``safe-structural`` (booleans/enums such as
    ``paid``, ``captured``, ``status``, ``livemode``). Empty/whitespace names
    classify as structural rather than raising, so a malformed export cannot crash
    the pass.
    """
    n = (field_name or "").strip().lower()
    if not n:
        return CAT_STRUCTURAL
    leaf = n.split(".")[-1]
    while leaf.endswith("[]"):
        leaf = leaf[:-2]
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


def iter_record_paths(obj: object, prefix: str = ""):
    """Yield ``(dotted_path, json_type)`` pairs for one record's structure.

    Recurses into dictionaries (dotted child paths) and lists (``[]`` marker),
    distinguishing a container path (type ``dict``/``list``) from its child
    fields. **Only types are yielded — never a value.** Free-text and scalar
    values are represented solely by their JSON type, so no arbitrary content is
    emitted. Nulls, dicts, lists, and scalars are all handled safely; a non-dict
    list item contributes only its type.
    """
    if isinstance(obj, dict):
        if prefix:
            yield (prefix, "dict")
        for key, value in obj.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from iter_record_paths(value, child)
    elif isinstance(obj, list):
        if prefix:
            yield (prefix, "list")
        item_path = f"{prefix}[]" if prefix else "[]"
        for item in obj:
            if isinstance(item, (dict, list)):
                yield from iter_record_paths(item, item_path)
            else:
                yield (item_path, _json_type(item))
    else:
        if prefix:
            yield (prefix, _json_type(obj))


def safe_field_report(records: list) -> list[dict]:
    """Return sanitized per-path structure for a list of Stripe records.

    Each entry: ``{field, category, types, present_pct}``. Presence is counted
    per record (a path present many times in one record still counts once).
    Non-dict list entries are skipped safely. **Values are never included.**
    """
    n = len(records)
    if n == 0:
        return []
    present: dict[str, int] = defaultdict(int)
    types: dict[str, set] = defaultdict(set)
    for r in records:
        if not isinstance(r, dict):
            continue  # malformed record: contribute nothing, never expose
        seen: set[str] = set()
        for path, jtype in iter_record_paths(r, ""):
            types[path].add(jtype)
            seen.add(path)
        for path in seen:
            present[path] += 1
    out = []
    for field in sorted(present):
        out.append(
            {
                "field": field,
                "category": categorize_field(field),
                "types": sorted(types[field]),
                "present_pct": round(100 * present[field] / n, 1),
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

    # Aggregate object-type distribution (record['object']) — type NAMES only.
    obj_types: dict[str, int] = defaultdict(int)
    for r in records:
        obj_types[r.get("object", "?")] += 1

    report = safe_field_report(records)
    cat_counts: dict[str, int] = defaultdict(int)
    for row in report:
        cat_counts[row["category"]] += 1

    print("No production record value is published. Only sanitized structure and")
    print("aggregate characteristics are reported.\n")
    print(f"Aggregate: {len(records)} record(s); object types: {dict(obj_types)}")
    print(f"Distinct field paths (incl. nested): {len(report)}")
    print("Paths by privacy category (names only):")
    for cat in sorted(cat_counts):
        print(f"  {cat:24} {cat_counts[cat]:>3}")
    print("\nField structure (paths + category + type + presence; NO VALUES):")
    print(f"  {'path':40} {'category':24} {'present%':>8}  types")
    for row in report:
        print(f"  {row['field']:40} {row['category']:24} {row['present_pct']:7.1f}%  {row['types']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
