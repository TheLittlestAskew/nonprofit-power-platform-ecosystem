"""Unit tests for the Web Resources example validator and source-backed examples.

All fixtures are INVENTED. These exercise ``scan_text`` and ``validate_tree`` from
``scripts/validate_web_resource_examples.py`` (scope-aware: strict for JS, relaxed
for Markdown) and assert structural markers of the source-backed reconciliations.

Run with:  python -m pytest tests/ -q
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_web_resource_examples as vwr  # noqa: E402

EXAMPLES = REPO_ROOT / "web-resources" / "examples"
_NOTICE = "/** SANITIZED EXAMPLE */\n"


def _clean_js():
    return _NOTICE + (
        '"use strict";\n'
        "const attr = formContext.getAttribute('sample_person');\n"
        "await Xrm.WebApi.retrieveRecord('sample_people', id, '?$select=sample_summary');\n"
        "const role = 'Sample Administrator';\n"
    )


# --------------------------------------------------------------------------- #
# JavaScript: strict rules
# --------------------------------------------------------------------------- #

def test_js_flags_guid():
    assert any("GUID" in p for p in vwr.scan_text("x.js", _NOTICE + "id='12345678-1234-1234-1234-123456789abc';", True))


def test_js_flags_schema_prefix():
    assert any("schema prefix" in p for p in vwr.scan_text("x.js", _NOTICE + "getAttribute('tr_widget');", True))
    assert any("schema prefix" in p for p in vwr.scan_text("x.js", _NOTICE + "getAttribute('new_customfield');", True))


def test_js_flags_env_url():
    assert any("environment/URL" in p for p in vwr.scan_text("x.js", _NOTICE + "u='https://x.crm.dynamics.com/api';", True))


def test_js_flags_non_fictional_email():
    assert any("email domain" in p for p in vwr.scan_text("x.js", _NOTICE + "// person@realmail.org", True))


def test_js_allows_reserved_email():
    assert not any("email domain" in p for p in vwr.scan_text("x.js", _NOTICE + "// a@example.invalid", True))


def test_js_flags_production_role_name():
    assert any("role name" in p for p in vwr.scan_text("x.js", _NOTICE + 'const r="Regional Payroll Administrator";', True))


def test_js_allows_sample_role_name():
    assert not any("role name" in p for p in vwr.scan_text("x.js", _NOTICE + 'const r="Sample Administrator";', True))


def test_js_flags_forbidden_terms():
    for term in ("guest", "payroll", "discharge", "ssn", "medication"):
        assert any("forbidden sensitive term" in p for p in vwr.scan_text("x.js", _NOTICE + f"// {term} logic", True)), term


def test_js_missing_notice_flagged():
    assert any("missing" in p for p in vwr.scan_text("x.js", "const a=1;", True))


def test_js_sync_network_flagged():
    for snip in ("new XMLHttpRequest();", "async: false", "new ActiveXObject('X')"):
        assert any("synchronous network" in p for p in vwr.scan_text("x.js", _NOTICE + snip, True)), snip


def test_js_flags_source_private():
    assert any("source-private" in p for p in vwr.scan_text("x.js", _NOTICE + "// from source-private/foo", True))


def test_js_flags_original_filename():
    assert any("original source filename" in p for p in vwr.scan_text("x.js", _NOTICE + "// see original.txt", True))


def test_js_clean_passes():
    assert vwr.scan_text("clean.js", _clean_js(), True) == []


# --------------------------------------------------------------------------- #
# Markdown: relaxed but still safe
# --------------------------------------------------------------------------- #

def test_md_allows_source_private_mention():
    # Docs MAY reference the documented source-private boundary.
    assert vwr.scan_text("doc.md", "Originals live in source-private/ and are never committed.", False) == []


def test_md_allows_high_level_domain_terms():
    # High-level operational domains are not secrets by themselves in docs.
    problems = vwr.scan_text("doc.md", "These scripts supported shelter operations and case management.", False)
    assert not any("forbidden" in p for p in problems)


def test_md_allows_doc_links():
    md = "See [docs](https://learn.microsoft.com/power-apps) for the Client API."
    assert not any("URL" in p or "endpoint" in p for p in vwr.scan_text("doc.md", md, False))


def test_md_rejects_guid():
    assert any("GUID" in p for p in vwr.scan_text("doc.md", "form 12345678-1234-1234-1234-123456789abc", False))


def test_md_rejects_schema_prefix():
    assert any("schema prefix" in p for p in vwr.scan_text("doc.md", "the `tr_guestname` column", False))


def test_md_rejects_env_endpoint_url():
    assert any("endpoint" in p for p in vwr.scan_text("doc.md", "https://contoso.crm.dynamics.com/api/data/v9.2", False))


def test_md_rejects_original_filename():
    assert any("original source filename" in p for p in vwr.scan_text("doc.md", "reconstructed from original_export.txt", False))


def test_md_rejects_non_fictional_email():
    assert any("email domain" in p for p in vwr.scan_text("doc.md", "contact staff@realorg.org", False))


# --------------------------------------------------------------------------- #
# Structural coverage of the source-backed reconciliations
# --------------------------------------------------------------------------- #

def _read(example):
    return (EXAMPLES / example).read_text(encoding="utf-8")


def test_form_routing_is_source_backed():
    t = _read("form-routing.js")
    assert "ensureMainFormForExistingOnly" in t and "ensureIntakeFormForNewOnly" in t
    assert "Xrm.Navigation.navigateTo" in t
    assert "is_returning" not in t and "returningFlag" not in t  # invented flag removed


def test_duplicate_prevention_no_window_and_fails_closed():
    t = _read("duplicate-prevention.js")
    assert "INTENTIONAL DEVIATION" in t and "fail-closed" in t.lower()
    assert "windowHours" not in t and "24 * 60" not in t  # invented date window removed


def test_autofill_uses_webapi_retrieve_and_expand():
    t = _read("returning-record-autofill.js")
    assert "Xrm.WebApi.retrieveRecord" in t and "$expand" in t
    assert "sample_requires_review" in t
    # No actual raw-fetch call (a docstring may still NOTE the modernization).
    assert "await fetch(" not in t and "= fetch(" not in t


def test_datetime_is_lookup_driven_not_duration():
    t = _read("date-time-validation.js")
    assert "Xrm.WebApi.retrieveRecord" in t and "toDateString" in t
    assert "durationMinutes" not in t and "computeEnd" not in t  # duration approach removed


def test_flow_refresh_waits_for_id_and_has_alternative():
    t = _read("flow-refresh-coordination.js")
    assert "waitForRecordId" in t and "data.refresh(false)" in t
    assert "ALTERNATIVE" in t


def test_command_security_uses_security_role_ids():
    t = _read("command-security.js")
    assert "userSettings.securityRoles" in t
    assert "SAMPLE_ADMIN_ROLE_ID" in t and "SAMPLE_REVIEWER_ROLE_ID" in t


# --------------------------------------------------------------------------- #
# The committed web-resources tree must pass
# --------------------------------------------------------------------------- #

def test_committed_web_resources_tree_passes():
    assert vwr.validate_tree() == []
