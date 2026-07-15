#!/usr/bin/env python3
"""Validate the public development-finance sample records.

Guarantees ``development-finance/sample-records.json`` is safe to publish: it must
be flagged as sample data, contain only clearly-fictional values, demonstrate the
eight required reconciliation scenarios, and use only the reserved
``@example.invalid`` domain for any email-shaped value.

**No production record value is published.** This validator is a positive check
(required structure present) and a negative check (no real-looking identifier,
email domain, GUID, or card run).

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

# Real-data indicators. Sample values must never match these.
_REAL_STRIPE_ID = re.compile(r"\b(ch|po|cus|txn|pi|acct|tok|re|py)_[A-Za-z0-9]{8,}\b")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")

# The ONLY email domain permitted in the committed sample (RFC 6761 reserved).
_ALLOWED_EMAIL_DOMAIN = "example.invalid"

# A fictional value must be recognizable as invented.
_FICTION_MARKERS = ("SAMPLE", "FICTIONAL", "EXAMPLE")

# Structures the sample must demonstrate (non-empty top-level lists).
_REQUIRED_SECTIONS = ("deposits", "transactions", "scenarios")

# The eight reconciliation scenarios that must each appear in ``scenarios``.
_REQUIRED_SCENARIOS = frozenset({
    "high_confidence_auto_match",
    "lower_confidence_review",
    "unmatched",
    "multiple_candidate_ambiguity",
    "duplicate_detected",
    "payout_as_deposit",
    "transaction_linked_to_deposit",
    "reconciled_relationship",
})


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


def _email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].strip().lower()


def scan_for_real_identifiers(doc) -> list[str]:
    """Return problems if any real-looking identifier or email domain appears.

    Emails are rejected by default; an address whose domain is exactly
    ``example.invalid`` is allowed. Any other domain (``example.com``, real
    domains) is flagged. Real Stripe id patterns, GUIDs, and card-like digit runs
    are always flagged. Fictional sample ids (e.g. ``SAMPLE-CHG-001``) do not
    match these.
    """
    problems: list[str] = []
    for s in _walk_strings(doc):
        for m in _EMAIL.finditer(s):
            if _email_domain(m.group(0)) != _ALLOWED_EMAIL_DOMAIN:
                problems.append(f"email domain not '@{_ALLOWED_EMAIL_DOMAIN}' in a sample string")
        if _REAL_STRIPE_ID.search(s):
            problems.append("real-looking Stripe id pattern in a sample string")
        if _GUID.search(s):
            problems.append("GUID pattern in a sample string")
        if _CARD.search(s):
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

    for key in _REQUIRED_SECTIONS:
        val = doc.get(key)
        if not isinstance(val, list) or not val:
            problems.append(f"required section '{key}' missing or empty")

    # Every deposit/transaction/scenario id should carry a fiction marker.
    for section in ("deposits", "transactions", "scenarios"):
        for i, rec in enumerate(doc.get(section, []) or []):
            rid = rec.get("id", "") if isinstance(rec, dict) else ""
            if not any(m in str(rid).upper() for m in _FICTION_MARKERS):
                problems.append(f"{section}[{i}] id '{rid}' lacks a fiction marker (e.g. SAMPLE-)")

    # All eight reconciliation scenarios must be present.
    present = {
        rec.get("scenario") for rec in (doc.get("scenarios", []) or []) if isinstance(rec, dict)
    }
    for name in sorted(_REQUIRED_SCENARIOS - present):
        problems.append(f"missing required scenario: '{name}'")

    # A reconciled relationship must actually declare a reconciliation status.
    for i, rec in enumerate(doc.get("scenarios", []) or []):
        if isinstance(rec, dict) and rec.get("scenario") == "reconciled_relationship":
            if not rec.get("reconciliation_status"):
                problems.append(f"scenarios[{i}] 'reconciled_relationship' missing 'reconciliation_status'")

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
    print(f"OK: {SAMPLE_FILE.relative_to(REPO_ROOT)} is valid, fictional, and complete "
          f"(all {len(_REQUIRED_SCENARIOS)} scenarios present).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
