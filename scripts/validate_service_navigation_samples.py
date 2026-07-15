#!/usr/bin/env python3
"""Validate the public service-navigation module for structure and privacy.

Three passes:

1. **Fictional samples** — ``service-navigation/fictional-samples.json`` must
   be flagged as sample data, use fiction-marked identifiers, demonstrate the
   required scenarios (multi-program organization, multi-category resource,
   three-level Goal → Action Item → Need pathway, multiple Action Items, an
   Action Item with multiple Needs, an optional step, a resource-linked
   pathway, and an individualized copy with status fields), and keep the
   hierarchy internally consistent (parent references, code depth, prefixes).
2. **Data dictionary** — ``service-navigation/data-dictionary.csv`` must have
   the expected columns and use only the approved production-value-treatment
   labels.
3. **Privacy scan** — every public file in the module (plus the architecture
   diagram) is scanned for leakage patterns: GUIDs, checksum/base64-like runs,
   emails outside the reserved ``example.invalid`` domain, phone-like digit
   runs, URLs outside ``example.invalid``, and production schema prefixes.
   Relative Markdown links must resolve and Mermaid blocks must declare a
   diagram type.

**No production record value is published.** All checks run against public
files only; the private exports are never read by this validator.

Usage:
    python scripts/validate_service_navigation_samples.py

Exits non-zero (with the list of problems) if any check fails.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "service-navigation"
SAMPLE_FILE = MODULE_DIR / "fictional-samples.json"
DICTIONARY_FILE = MODULE_DIR / "data-dictionary.csv"
ARCHITECTURE_FILE = REPO_ROOT / "architecture" / "service-navigation-lifecycle.md"

# ---------------------------------------------------------------------------
# Leakage patterns. Public module text must never match these.
# ---------------------------------------------------------------------------

_GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
_CHECKSUM = re.compile(r"[A-Za-z0-9+/]{40,}={0,2}")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"\(?\d{3}\)?[ \-.]\d{3}[ \-.]\d{4}|\b\d{10,}\b")
_URL = re.compile(r"(?:https?|ftp)://([^/\s\")\]>]+)", re.IGNORECASE)
_SCHEMA_PREFIX = re.compile(r"\b(?:tr|msnfp|msiati|new)_[A-Za-z]")
_STREET_ADDRESS = re.compile(
    r"\b\d{1,5}\s+\w+(?:\s\w+)?\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Highway|Hwy)\b\.?",
    re.IGNORECASE,
)

_ALLOWED_EMAIL_DOMAIN = "example.invalid"
_ALLOWED_URL_HOST = "example.invalid"
_FICTION_MARKERS = ("SAMPLE", "FICTIONAL", "EXAMPLE")

_ALLOWED_TREATMENTS = frozenset({
    "Never publish",
    "Aggregate only",
    "Generalized structure only",
    "Fictional sample permitted",
    "Public taxonomy label only after review",
})
_DICTIONARY_COLUMNS = [
    "Public Field", "Public Entity", "Description", "Data Type", "Required?",
    "Relationship", "Source Concept", "Production Value Treatment", "Notes",
]

_ALLOWED_PLAN_STATUSES = frozenset({
    "not started", "in progress", "blocked", "complete", "skipped-optional",
})

_TYPE_DEPTH = {"Goal": 1, "Action Item": 2, "Need": 3}
_PARENT_TYPE = {"Action Item": "Goal", "Need": "Action Item"}


def _walk_strings(obj):
    """Yield every string value found anywhere in a JSON structure."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from _walk_strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _walk_strings(value)


def scan_text(text: str, where: str) -> list[str]:
    """Leakage scan for one blob of public text. Returns problems."""
    problems: list[str] = []
    if _GUID.search(text):
        problems.append(f"{where}: GUID pattern present")
    if _CHECKSUM.search(text):
        problems.append(f"{where}: checksum/base64-like run present")
    for match in _EMAIL.finditer(text):
        domain = match.group(0).rsplit("@", 1)[-1].strip().lower()
        if domain != _ALLOWED_EMAIL_DOMAIN:
            problems.append(f"{where}: email domain not '@{_ALLOWED_EMAIL_DOMAIN}'")
    if _PHONE.search(text):
        problems.append(f"{where}: phone-like digit run present")
    for match in _URL.finditer(text):
        host = match.group(1).split(":")[0].lower()
        if host != _ALLOWED_URL_HOST:
            problems.append(f"{where}: URL host '{host}' is not '{_ALLOWED_URL_HOST}'")
    if _SCHEMA_PREFIX.search(text):
        problems.append(f"{where}: production schema prefix present")
    if _STREET_ADDRESS.search(text):
        problems.append(f"{where}: street-address-like value present")
    return problems


# ---------------------------------------------------------------------------
# Pass 1 — fictional samples.
# ---------------------------------------------------------------------------

def _fiction_marked(value: object) -> bool:
    return any(marker in str(value).upper() for marker in _FICTION_MARKERS)


def validate_template_hierarchy(pathway: dict, where: str) -> list[str]:
    """Structural checks for one template pathway. Returns problems."""
    problems: list[str] = []
    steps = pathway.get("steps")
    if not isinstance(steps, list) or not steps:
        return [f"{where}: 'steps' missing or empty"]

    by_id = {}
    for i, step in enumerate(steps):
        step_id = step.get("id")
        if not step_id or not _fiction_marked(step_id):
            problems.append(f"{where}.steps[{i}]: id missing or lacks a fiction marker")
        if step_id in by_id:
            problems.append(f"{where}.steps[{i}]: duplicate id")
        by_id[step_id] = step

    for i, step in enumerate(steps):
        step_type = step.get("step_type")
        code = str(step.get("step_code", ""))
        if step_type not in _TYPE_DEPTH:
            problems.append(f"{where}.steps[{i}]: step_type {step_type!r} not Goal/Action Item/Need")
            continue
        segments = [s for s in code.split(".") if s]
        if len(segments) != _TYPE_DEPTH[step_type]:
            problems.append(f"{where}.steps[{i}]: step_code depth {len(segments)} "
                            f"does not match type {step_type!r}")
        parent_id = step.get("parent")
        if step_type == "Goal":
            if parent_id is not None:
                problems.append(f"{where}.steps[{i}]: Goal must have parent null")
            continue
        parent = by_id.get(parent_id)
        if parent is None:
            problems.append(f"{where}.steps[{i}]: parent {parent_id!r} not found")
            continue
        if parent.get("step_type") != _PARENT_TYPE[step_type]:
            problems.append(f"{where}.steps[{i}]: parent type {parent.get('step_type')!r} "
                            f"is not {_PARENT_TYPE[step_type]!r}")
        parent_code = str(parent.get("step_code", ""))
        if parent_code and not code.startswith(parent_code + "."):
            problems.append(f"{where}.steps[{i}]: step_code does not extend the parent's code")
        if "optional_step" not in step or not isinstance(step["optional_step"], bool):
            problems.append(f"{where}.steps[{i}]: optional_step must be an explicit boolean")
    return problems


def validate_samples(doc) -> list[str]:
    """Structural + scenario + safety validation of the sample document."""
    problems: list[str] = []
    if not isinstance(doc, dict):
        return ["top-level JSON is not an object"]
    if doc.get("sample_data") is not True:
        problems.append("missing or false 'sample_data': true flag")
    if "FICTIONAL" not in str(doc.get("_notice", "")).upper():
        problems.append("'_notice' must state records are fictional")

    for section, minimum in (("organizations", 2), ("resources", 3),
                             ("pathway_templates", 1), ("individual_plans", 1)):
        items = doc.get(section)
        if not isinstance(items, list) or len(items) < minimum:
            problems.append(f"required section '{section}' missing or has fewer than {minimum} entries")

    resources = [r for r in doc.get("resources", []) or [] if isinstance(r, dict)]
    for section in ("organizations", "resources"):
        for i, record in enumerate(doc.get(section, []) or []):
            if isinstance(record, dict) and not _fiction_marked(record.get("id", "")):
                problems.append(f"{section}[{i}]: id lacks a fiction marker (e.g. SAMPLE-)")

    # One organization must operate multiple programs.
    by_org: dict[str, int] = {}
    for resource in resources:
        org = str(resource.get("organization_title", ""))
        by_org[org] = by_org.get(org, 0) + 1
    if not any(count >= 2 for count in by_org.values()):
        problems.append("no organization operates multiple programs in the samples")

    # Resources must span more than one category, and one resource must be
    # multi-category.
    all_categories = {c for r in resources for c in (r.get("top_level_categories") or [])}
    if len(all_categories) < 2:
        problems.append("resources do not span more than one category")
    if not any(len(r.get("top_level_categories") or []) > 1 for r in resources):
        problems.append("no multi-category resource in the samples")

    resource_ids = {r.get("id") for r in resources}
    templates = [t for t in doc.get("pathway_templates", []) or [] if isinstance(t, dict)]
    linked = False
    optional_seen = False
    multi_action = False
    multi_need = False
    three_level = False
    for t_index, template in enumerate(templates):
        where = f"pathway_templates[{t_index}]"
        problems.extend(validate_template_hierarchy(template, where))
        steps = [s for s in template.get("steps", []) or [] if isinstance(s, dict)]
        if template.get("linked_resource") in resource_ids:
            linked = True
        actions = [s for s in steps if s.get("step_type") == "Action Item"]
        needs = [s for s in steps if s.get("step_type") == "Need"]
        if any(s.get("optional_step") is True for s in steps):
            optional_seen = True
        if len(actions) >= 2:
            multi_action = True
        if any(sum(1 for n in needs if n.get("parent") == a.get("id")) >= 2 for a in actions):
            multi_need = True
        if any(s.get("step_type") == "Goal" for s in steps) and actions and needs:
            three_level = True
    if not linked:
        problems.append("no pathway template links to a sample resource")
    if not optional_seen:
        problems.append("no optional step demonstrated")
    if not multi_action:
        problems.append("no pathway with multiple Action Items")
    if not multi_need:
        problems.append("no Action Item with multiple Needs")
    if not three_level:
        problems.append("no three-level Goal -> Action Item -> Need pathway")

    # Individualized copies must reference the template and carry status.
    template_step_ids = {s.get("id") for t in templates for s in (t.get("steps") or [])
                         if isinstance(s, dict)}
    for p_index, plan in enumerate(doc.get("individual_plans", []) or []):
        if not isinstance(plan, dict):
            continue
        where = f"individual_plans[{p_index}]"
        plan_steps = [s for s in plan.get("steps", []) or [] if isinstance(s, dict)]
        if not plan_steps:
            problems.append(f"{where}: has no steps")
            continue
        plan_ids = {s.get("id") for s in plan_steps}
        for s_index, step in enumerate(plan_steps):
            if step.get("copied_from") not in template_step_ids:
                problems.append(f"{where}.steps[{s_index}]: copied_from does not reference a template step")
            status = step.get("plan_status")
            if status not in _ALLOWED_PLAN_STATUSES:
                problems.append(f"{where}.steps[{s_index}]: plan_status {status!r} not in allowed set")
            parent = step.get("parent")
            if parent is not None and parent not in plan_ids:
                problems.append(f"{where}.steps[{s_index}]: parent must reference a copied plan step")

    # Safety scan over every string in the document.
    problems.extend(scan_text("\n".join(_walk_strings(doc)), "fictional-samples.json"))
    return problems


# ---------------------------------------------------------------------------
# Pass 2 — data dictionary.
# ---------------------------------------------------------------------------

def validate_dictionary(text: str) -> list[str]:
    """Structural validation of the public data dictionary CSV."""
    problems: list[str] = []
    rows = list(csv.reader(text.splitlines()))
    if not rows:
        return ["data dictionary is empty"]
    if rows[0] != _DICTIONARY_COLUMNS:
        problems.append("data dictionary header does not match the expected columns")
        return problems
    if len(rows) < 2:
        problems.append("data dictionary has no field rows")
    treatment_col = _DICTIONARY_COLUMNS.index("Production Value Treatment")
    for line_number, row in enumerate(rows[1:], start=2):
        if len(row) != len(_DICTIONARY_COLUMNS):
            problems.append(f"data dictionary line {line_number}: wrong column count")
            continue
        for required in ("Public Field", "Public Entity", "Description", "Production Value Treatment"):
            if not row[_DICTIONARY_COLUMNS.index(required)].strip():
                problems.append(f"data dictionary line {line_number}: '{required}' is empty")
        if row[treatment_col].strip() not in _ALLOWED_TREATMENTS:
            problems.append(f"data dictionary line {line_number}: treatment "
                            f"'{row[treatment_col]}' not in the approved label set")
    return problems


# ---------------------------------------------------------------------------
# Pass 3 — privacy scan + link/diagram checks over public module files.
# ---------------------------------------------------------------------------

_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)[^)]*\)")
_MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
_MERMAID_TYPES = ("flowchart", "graph", "sequenceDiagram", "erDiagram", "classDiagram")


def public_files() -> list[Path]:
    files = sorted(p for p in MODULE_DIR.rglob("*") if p.is_file())
    if ARCHITECTURE_FILE.exists():
        files.append(ARCHITECTURE_FILE)
    return files


def check_markdown(path: Path, text: str) -> list[str]:
    """Relative links must resolve; Mermaid blocks must declare a type."""
    problems: list[str] = []
    for target in _MD_LINK.findall(text):
        if re.match(r"^[a-z]+:", target):  # absolute URL — handled by scan_text
            continue
        if not (path.parent / target).resolve().exists():
            problems.append(f"{path.name}: broken relative link '{target}'")
    for block in _MERMAID_BLOCK.findall(text):
        first = block.strip().splitlines()[0].strip() if block.strip() else ""
        if not first.startswith(_MERMAID_TYPES):
            problems.append(f"{path.name}: mermaid block does not declare a known diagram type")
    return problems


def validate_module() -> list[str]:
    problems: list[str] = []

    if not SAMPLE_FILE.exists():
        problems.append("fictional-samples.json is missing")
    else:
        try:
            problems.extend(validate_samples(json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))))
        except json.JSONDecodeError as exc:
            problems.append(f"fictional-samples.json is not valid JSON: {exc}")

    if not DICTIONARY_FILE.exists():
        problems.append("data-dictionary.csv is missing")
    else:
        problems.extend(validate_dictionary(DICTIONARY_FILE.read_text(encoding="utf-8")))

    for path in public_files():
        text = path.read_text(encoding="utf-8")
        where = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        problems.extend(scan_text(text, where))
        if path.suffix == ".md":
            problems.extend(check_markdown(path, text))
    return problems


def main() -> int:
    problems = validate_module()
    if problems:
        sys.stderr.write("Service-navigation validation FAILED:\n")
        for problem in problems:
            sys.stderr.write(f"  - {problem}\n")
        return 1
    file_count = len(public_files())
    print(f"OK: service-navigation module is valid, fictional, and clean "
          f"({file_count} public files scanned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
