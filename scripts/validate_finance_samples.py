#!/usr/bin/env python3
"""Validate the public development-finance sample records.

Checks ``development-finance/sample-records.json`` to guarantee it is safe to
publish: it must be flagged as sample data, must contain only clearly-fictional
values, and must demonstrate the reconciliation structures the module documents
(deposit, transaction, donor match, and exception).

This validator is what keeps invented demonstration data from ever drifting into
something that resembles production. It is a **positive** check (required
structure present) and a **negative** check (no real-looking identifiers).

Usage:
    python scripts/validate_finance_samples.py

Exits non-zero (with the list of problems) if any check fails.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = REPO_ROOT / "development-finance" / "sample-records.json"

# Patterns that would indicate REAL processor / personal data leaked into a
# sample. Sample values must never match these.
_REAL_STRIPE_ID = re.compile(r"\b(ch|po|cus|txn|pi|acct|tok|re|py)_[A-Za-z0-9]{8,}\b")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")

# A fictional value must be recognizable as invented. We accept these markers.
_FICTION_MARKERS = ("SAMPLE", "FICTIONAL", "EXAMPLE", "sample")

# Structures the sample must demonstrate (top-level keys).
_REQUIRED_KEYS = ("deposits", "transactions", "donor_match_examples", "exception_examples")


def _walk_strings(obj):
    """Yield every string value found anywhere in a JSON structure."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_strings(v)


def scan_for_real_identifiers(doc) -> list[str]:
    """Return a list of problems if any real-looking identifier appears.

    Flags real Stripe id patterns, email addresses, GUIDs, and card-like digit
    runs. Fictional sample ids (e.g. ``SAMPLE-CHG-001``) do not match these.
    """
    problems: list[str] = []
    for s in _walk_strings(doc):
        if _REAL_STRIPE_ID.search(s):
            problems.append(f"real-looking Stripe id pattern in a sample string (len={len(s)})")
        if _EMAIL.search(s):
            problems.append("email-address pattern in a sample string")
        if _GUID.search(s):
            problems.append("GUID pattern in a sample string")
        if _CARD.search(s) and any(c.isdigit() for c in s):
            # Avoid flagging short ids; only long digit runs.
            digits = re.sub(r"\D", "", s)
            if len(digits) >= 13:
                problems.append("card-like digit run in a sample string")
    return problems


def validate_samples(doc) -> list[str]:
    """Structural + safety validation of the sample document. Returns problems."""
    problems: list[str] = []

    if not isinstance(doc, dict):
        return ["top-level JSON is not an object"]

    if doc.get("sample_data") is not True:
        problems.append("missing or false 'sample_data': true flag")

    for key in _REQUIRED_KEYS:
        val = doc.get(key)
        if not isinstance(val, list) or not val:
            problems.append(f"required section '{key}' missing or empty")

    # Every deposit/transaction id should carry a fiction marker.
    for section in ("deposits", "transactions"):
        for i, rec in enumerate(doc.get(section, []) or []):
            rid = rec.get("id", "") if isinstance(rec, dict) else ""
            if not any(m in str(rid) for m in _FICTION_MARKERS):
                problems.append(f"{section}[{i}] id '{rid}' lacks a fiction marker (e.g. SAMPLE-)")

    # Behavioral/PII demonstration must stay generalized: match examples should
    # describe a signal, not a real person.
    for i, rec in enumerate(doc.get("donor_match_examples", []) or []):
        if isinstance(rec, dict) and "match_signal" not in rec:
            problems.append(f"donor_match_examples[{i}] missing 'match_signal' (keep matching generalized)")

    problems.extend(scan_for_real_identifiers(doc))
    return problems


def main() -> int:
    if not SAMPLE_FILE.exists():
        sys.stderr.write(f"ERROR: sample file not found: {SAMPLE_FILE}\n")
        return 1
    try:
        doc = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"ERROR: {SAMPLE_FILE} is not valid JSON: {exc}\n")
        return 1

    problems = validate_samples(doc)
    if problems:
        sys.stderr.write("Sample validation FAILED:\n")
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
        return 1
    print(f"OK: {SAMPLE_FILE.relative_to(REPO_ROOT)} is valid, fictional, and complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
