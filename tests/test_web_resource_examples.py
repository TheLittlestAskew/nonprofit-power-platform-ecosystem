"""Unit tests for the Web Resources example validator.

All fixtures are INVENTED. These exercise ``scan_text`` and ``validate_tree``
from ``scripts/validate_web_resource_examples.py`` and assert that the committed
``web-resources/`` examples pass.

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_web_resource_examples as vwr  # noqa: E402

_NOTICE = "/** SANITIZED EXAMPLE */\n"


def _clean_js():
    return _NOTICE + (
        '"use strict";\n'
        "const attr = formContext.getAttribute('sample_person');\n"
        "await Xrm.WebApi.retrieveMultipleRecords('sample_related_records', '?$top=1');\n"
        "const role = 'Sample Administrator';\n"
    )


# --------------------------------------------------------------------------- #
# Negative checks (each forbidden category must be rejected)
# --------------------------------------------------------------------------- #

def test_flags_guid():
    problems = vwr.scan_text("x.js", _NOTICE + "const id='12345678-1234-1234-1234-123456789abc';", True)
    assert any("GUID" in p for p in problems)


def test_flags_schema_prefix_tr():
    problems = vwr.scan_text("x.js", _NOTICE + "getAttribute('tr_guestname');", True)
    assert any("schema prefix" in p for p in problems)


def test_flags_schema_prefix_new():
    problems = vwr.scan_text("x.js", _NOTICE + "getAttribute('new_customfield');", True)
    assert any("schema prefix" in p for p in problems)


def test_flags_env_url_in_js():
    problems = vwr.scan_text("x.js", _NOTICE + "const u='https://contoso.crm.dynamics.com/api';", True)
    assert any("environment/URL" in p for p in problems)


def test_flags_non_fictional_email():
    problems = vwr.scan_text("x.js", _NOTICE + "// contact person@realmail.org", True)
    assert any("email domain" in p for p in problems)


def test_allows_reserved_email_domain():
    problems = vwr.scan_text("x.js", _NOTICE + "// contact sample@example.invalid", True)
    assert not any("email domain" in p for p in problems)


def test_flags_production_role_name():
    problems = vwr.scan_text("x.js", _NOTICE + 'const r = "Regional Payroll Administrator";', True)
    assert any("role name" in p for p in problems)


def test_allows_sample_role_name():
    problems = vwr.scan_text("x.js", _NOTICE + 'const r = "Sample Administrator";', True)
    assert not any("role name" in p for p in problems)


def test_flags_forbidden_term():
    for term in ("guest", "payroll", "discharge", "nightwatch", "ssn"):
        problems = vwr.scan_text("x.js", _NOTICE + f"// handles {term} logic", True)
        assert any("forbidden sensitive term" in p for p in problems), term


def test_missing_notice_flagged_for_js():
    problems = vwr.scan_text("x.js", "const a = 1;", True)
    assert any("missing" in p and "SANITIZED EXAMPLE" in p for p in problems)


def test_sync_network_flagged():
    for snippet in ("new XMLHttpRequest();", "async: false", "new ActiveXObject('X')"):
        problems = vwr.scan_text("x.js", _NOTICE + snippet, True)
        assert any("synchronous network" in p for p in problems), snippet


def test_source_private_path_flagged():
    problems = vwr.scan_text("x.js", _NOTICE + "// derived from source-private/web-resources/foo", True)
    assert any("private source path" in p for p in problems)


def test_txt_source_reference_flagged():
    problems = vwr.scan_text("x.js", _NOTICE + "// see original.txt", True)
    assert any("private source path" in p for p in problems)


# --------------------------------------------------------------------------- #
# Positive checks
# --------------------------------------------------------------------------- #

def test_clean_js_passes():
    assert vwr.scan_text("clean.js", _clean_js(), True) == []


def test_markdown_allows_https_links():
    # A docs URL in a .md file is allowed (not a JS example).
    md = "See [docs](https://learn.microsoft.com/power-apps) for the Client API."
    assert not any("environment/URL" in p for p in vwr.scan_text("doc.md", md, False))


# --------------------------------------------------------------------------- #
# The committed web-resources tree must pass
# --------------------------------------------------------------------------- #

def test_committed_web_resources_tree_passes():
    assert vwr.validate_tree() == []
