#!/usr/bin/env python3
"""Validate the public Web Resources examples for privacy and quality.

Scans ``web-resources/`` and rejects anything that would leak production detail or
regress the sanitized-example contract:

* GUID patterns
* organization-specific schema prefixes (``tr_``, ``new_``, ``msnfp_`` …)
* environment URLs (in JavaScript examples)
* email addresses outside the reserved fictional domains
* production-looking security-role names (role strings must be ``Sample …``)
* forbidden sensitive terminology (guest, shelter, payroll, clinical, …)
* JavaScript examples missing the ``SANITIZED EXAMPLE`` notice
* legacy synchronous network calls
* private source paths referenced in public files

These are **structure/pattern** checks over the public files only; nothing in
``source-private/`` is read.

Usage:
    python scripts/validate_web_resource_examples.py

Exits non-zero (listing the problems) if any check fails.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WR_ROOT = REPO_ROOT / "web-resources"

# Reserved fictional email domains (RFC 2606 / 6761). Anything else is rejected.
_ALLOWED_EMAIL_DOMAINS = frozenset({"example.invalid", "example.test", "example.com"})

_GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
# Organization-specific publisher prefixes. 'sample_' is the approved fictional
# prefix and is intentionally excluded.
_SCHEMA_PREFIX = re.compile(r"\b(tr_|new_|msnfp_|msiati_|adx_|cr[0-9a-f]{2,}_)[a-z][a-z0-9_]*", re.IGNORECASE)
_ENV_URL = re.compile(r"https?://[^\s\"')]+", re.IGNORECASE)
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_SYNC_NET = re.compile(r"XMLHttpRequest|ActiveXObject|async\s*:\s*false", re.IGNORECASE)
_SANITIZED_NOTICE = "SANITIZED EXAMPLE"
_SOURCE_PATH = re.compile(r"source-private|\.txt\b", re.IGNORECASE)

# Forbidden operational/sensitive terminology (word-boundary, case-insensitive).
_FORBIDDEN_TERMS = (
    "guest", "shelter", "payroll", "clinical", "behavioral", "discharge",
    "ssn", "social security", "nightwatch", "night watch", "eligibility",
    "medication", "diagnosis", "mental status", "veteran", "donor",
)
_FORBIDDEN_RE = re.compile(
    r"(?<![A-Za-z])(" + "|".join(re.escape(t) for t in _FORBIDDEN_TERMS) + r")(?![A-Za-z])",
    re.IGNORECASE,
)

# A role-name-looking string: Title Case words containing a role keyword. Real
# role names must be generalized, so any such string must begin with "Sample".
_ROLE_LIKE = re.compile(r'"([A-Z][A-Za-z]+(?:\s+[A-Za-z]+)*\s+(?:Administrator|Reviewer|Manager|Officer|Coordinator|Supervisor|Specialist|Role))"')


def _email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].strip().lower()


def scan_text(name: str, text: str, is_js: bool) -> list[str]:
    """Return a list of privacy/quality problems for one file's text."""
    problems: list[str] = []

    if _GUID.search(text):
        problems.append(f"{name}: GUID pattern present")

    m = _SCHEMA_PREFIX.search(text)
    if m:
        problems.append(f"{name}: organization schema prefix '{m.group(1)}…' present")

    for em in _EMAIL.finditer(text):
        if _email_domain(em.group(0)) not in _ALLOWED_EMAIL_DOMAINS:
            problems.append(f"{name}: non-fictional email domain present")

    fm = _FORBIDDEN_RE.search(text)
    if fm:
        problems.append(f"{name}: forbidden sensitive term '{fm.group(1).lower()}' present")

    if _SOURCE_PATH.search(text):
        problems.append(f"{name}: private source path/filename referenced")

    for rm in _ROLE_LIKE.finditer(text):
        if not rm.group(1).strip().lower().startswith("sample"):
            problems.append(f"{name}: production-looking role name '{rm.group(1)}' (use 'Sample …')")

    if is_js:
        if _SANITIZED_NOTICE not in text:
            problems.append(f"{name}: missing '{_SANITIZED_NOTICE}' notice")
        if _ENV_URL.search(text):
            problems.append(f"{name}: environment/URL present in a JS example")
        sm = _SYNC_NET.search(text)
        if sm:
            problems.append(f"{name}: legacy synchronous network call '{sm.group(0)}'")

    return problems


def validate_tree(root: Path = WR_ROOT) -> list[str]:
    """Validate every tracked-style text file under the web-resources tree."""
    problems: list[str] = []
    if not root.exists():
        return [f"web-resources directory not found: {root}"]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".js", ".md"):
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        problems.extend(scan_text(rel, text, is_js=path.suffix.lower() == ".js"))
    return problems


def main() -> int:
    problems = validate_tree()
    if problems:
        sys.stderr.write("Web-resource validation FAILED:\n")
        for p in problems:
            sys.stderr.write(f"  - {p}\n")
        return 1
    js_count = len(list(WR_ROOT.glob("examples/*.js"))) if WR_ROOT.exists() else 0
    print(f"OK: web-resources examples are sanitized and well-formed ({js_count} JS examples).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
