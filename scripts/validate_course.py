#!/usr/bin/env python3
"""Check lesson metadata, curriculum, navigation and local Markdown references.

Structural guardrail only: a passing run is NOT publisher-source review,
CEFR accreditation, accessibility audit, or user approval.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SKILLS = {"grammar", "vocabulary", "writing", "listening", "speaking", "pronunciation"}
LINKS = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
IMAGES = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMAGES = re.compile(r"<img\b[^>]*>", re.I)
HTML_ALT = re.compile(r"\balt\s*=\s*['\"][^'\"]+['\"]", re.I)
ERRORS = []


def fail(message):
    ERRORS.append(message)


def load_yaml(file):
    with file.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_curriculum():
    syllabus = load_yaml(ROOT / "curriculum/master_syllabus.yaml")
    schema = json.loads((ROOT / "curriculum/lesson_metadata.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    levels = syllabus.get("levels", [])
    if len(levels) != 7 or len({x["id"] for x in levels}) != 7:
        fail("Expected seven distinct editorial levels")
    if set(syllabus.get("assessment", {}).get("skills", [])) != SKILLS:
        fail("Six equally important skills must be present")
    ids = set()
    records = []
    for level in levels:
        letters = level.get("lessons_per_unit", [])
        if not letters or len(set(letters)) != len(letters):
            fail(f"{level['id']}: missing or duplicated lesson letters")
        units = level.get("units", [])
        if len({u["number"] for u in units}) != len(units):
            fail(f"{level['id']}: duplicate unit numbers")
        for unit in units:
            source_lessons = unit.get("source_lessons", [])
            if source_lessons:
                expected_source_lessons = {f"{unit['number']}{letter}" for letter in letters}
                actual_source_lessons = [item.get("source_lesson") for item in source_lessons]
                if set(actual_source_lessons) != expected_source_lessons or len(actual_source_lessons) != len(expected_source_lessons):
                    fail(f"{level['id']} Unit {unit['number']}: source index lesson labels incomplete or duplicated")
                for item in source_lessons:
                    if any(not isinstance(item.get(k), str) or not item[k].strip()
                           for k in ("title", "grammar", "vocabulary", "pronunciation")):
                        fail(f"{level['id']} Unit {unit['number']}: incomplete source index topic fields")
                    if item.get("source") != "user_supplied_index":
                        fail(f"{level['id']} Unit {unit['number']}: unexpected primary source label")
            for record in unit.get("lessons", []):
                lid = record.get("id", "<missing>")
                if lid in ids:
                    fail(f"Duplicate lesson ID: {lid}")
                ids.add(lid)
                records.append((level, unit, record))
                for issue in validator.iter_errors(record):
                    fail(f"{lid}: {issue.json_path}: {issue.message}")
                source = record.get("source_lesson", "")
                expected = f"{level['id']}.unit_{unit['number']:02}.lesson_{source[-1:].lower()}"
                if lid != expected or source != f"{unit['number']}{source[-1:]}":
                    fail(f"{lid}: source_lesson does not match level/unit/letter")
                if source[-1:] not in letters:
                    fail(f"{lid}: unexpected lesson letter")
                if set(record.get("skills", [])) != SKILLS:
                    fail(f"{lid}: six skills must be declared")
                if {a.get("skill") for a in record.get("oral_activities", [])} != {"listening", "speaking", "pronunciation"}:
                    fail(f"{lid}: oral handoff must include three skills")
                if not {"grammar", "vocabulary", "writing"}.issubset({a.get("skill") for a in record.get("objectives", [])}):
                    fail(f"{lid}: missing core written lesson objectives")
                alignment = record.get("cefr", {}).get("alignment")
                descriptor = record.get("cefr", {}).get("descriptor_reference")
                if (alignment == "descriptor_verified") != bool(descriptor):
                    fail(f"{lid}: verified CEFR alignment requires a reference; provisional alignment must not claim one")
                status = record.get("editorial_status")
                verification = record.get("source_verification")
                if verification == "pending_original_index" and (record.get("grammar") or record.get("vocabulary")):
                    fail(f"{lid}: source topics cannot be assigned without evidence")
                if status in {"approved", "published"} and verification == "pending_original_index":
                    fail(f"{lid}: cannot publish unverified source lesson")
                if verification == "source_index_confirmed":
                    if not any(src.get("type") == "user_supplied_index"
                               and src.get("verified_against_user_image") is True
                               and src.get("asset") and re.fullmatch(r"[a-f0-9]{64}", src.get("asset_sha256", ""))
                               for src in record.get("source_references", [])):
                        fail(f"{lid}: direct original-index verification requires a private asset fingerprint")
                    if not record.get("source_pronunciation"):
                        fail(f"{lid}: directly verified source lesson must record its pronunciation topics")
                if verification in {"external_index_confirmed", "source_index_confirmed"}:
                    if not record.get("source_references"):
                        fail(f"{lid}: confirmed source needs provenance")
                    for item in record.get("grammar", []) + record.get("vocabulary", []):
                        if item.get("origin") == "pending_source":
                            fail(f"{lid}: pending topic in confirmed source mapping")
    for level, unit, record in records:
        lid = record["id"]
        for dep in record.get("prerequisites", []):
            if dep not in ids:
                # Older lessons are not necessarily itemized yet; allow references
                # to declared unit/lesson combinations, not arbitrary IDs.
                m = re.fullmatch(r"([a-z_]+)\.unit_(\d{2})\.lesson_([a-z])", dep)
                lookup = next((x for x in levels if x["id"] == (m.group(1) if m else None)), None)
                if not (m and lookup and int(m.group(2)) in {u["number"] for u in lookup["units"]} and m.group(3).upper() in lookup["lessons_per_unit"]):
                    fail(f"{lid}: invalid prerequisite: {dep}")
                continue
            if dep == lid:
                fail(f"{lid}: cannot depend on itself")
    elementary = next((l for l in levels if l["id"] == "elementary"), None)
    if not elementary or [u["number"] for u in elementary["units"]] != list(range(1, 13)):
        fail("Elementary must retain 12 ordered units")
    if not elementary or elementary.get("lessons_per_unit") != ["A", "B", "C"]:
        fail("Elementary must retain three A/B/C lessons per unit")
    pre = next((l for l in levels if l["id"] == "pre_intermediate"), None)
    if pre and pre.get("coverage") == "complete_contents_index_available":
        indexed_assets = pre.get("index_provenance", {}).get("source_assets", [])
        if {x.get("source_page") for x in indexed_assets} != {2, 3} or any(
            not re.fullmatch(r"[a-f0-9]{64}", x.get("asset_sha256", ""))
            or not x.get("asset") for x in indexed_assets
        ):
            fail("Pre-intermediate original index needs two private image fingerprints")

        if [u["number"] for u in pre["units"]] != list(range(1, 13)):
            fail("Complete Pre-intermediate index must contain all twelve units")
        if sum(len(u.get("source_lessons", [])) for u in pre["units"]) != 36:
            fail("Complete Pre-intermediate index must enumerate 36 source lessons")
        sections = pre.get("source_sections", [])
        if len(sections) != 12:
            fail("Complete Pre-intermediate index must enumerate six Practical English and six Revise and Check sections")
        else:
            for i, section in enumerate(sections, 1):
                expected_type = "practical_english" if i % 2 else "revise_and_check"
                if section.get("after_unit") != i or section.get("type") != expected_type:
                    fail(f"Pre-intermediate source section after unit {i} is out of sequence")
        if pre.get("index_provenance", {}).get("source_content_storage") != "project_only_not_public_repository":
            fail("Original Pre-intermediate source images must remain private")
    if elementary:
        first = next((u for u in elementary["units"] if u["number"] == 1), {})
        if {r.get("id") for r in first.get("lessons", [])} != {
            "elementary.unit_01.lesson_a", "elementary.unit_01.lesson_b", "elementary.unit_01.lesson_c"
        }:
            fail("Elementary Unit 1 must have 1A/1B/1C")
    print(f"Checked {len(levels)} editorial levels and {len(records)} individual lesson records")


def local_target(md_path, raw):
    raw = raw.strip().split(" ", 1)[0].strip("<>")
    if not raw or raw.startswith("#") or raw.startswith("//"):
        return None
    url = urlsplit(raw)
    if url.scheme or url.netloc:
        return None
    relative = unquote(url.path)
    if not relative:
        return None
    return (DOCS / relative.lstrip("/")) if relative.startswith("/") else (md_path.parent / relative)


# Publication guard: check only built/public Markdown, not governance files.
# Match editorial phrases, not normal educational terms (review, practice, assessment).
EDITORIAL_LEAKS = [
    (re.compile(r"\b(?:editorial\s+draft|draft\s+pilot|draft\s+lesson|not\s+(?:yet\s+)?approved)\b", re.I),
     "obsolete draft/approval notice"),
    (re.compile(r"\b(?:development\s+branch|branch[- ]only|not\s+(?:yet\s+)?(?:publicly\s+)?deployed|not\s+(?:yet\s+)?published)\b", re.I),
     "obsolete development or publication notice"),
    (re.compile(r"\b(?:pull\s+request|PR\s*#\d+|squash\s+and\s+merge|editorial_status|asset_sha256)\b", re.I),
     "internal editorial metadata"),
    (re.compile(r"\b(?:elementary_[12]\.png|curriculum/master_syllabus\.yaml|feature/elementary-unit)\b", re.I),
     "private source or development-path disclosure"),
    (re.compile(r"\b(?:lesson\s+id\s*:|sha[- ]?256\b)\b", re.I),
     "technical identifiers"),
]


def frontmatter_and_body(content):
    """Return YAML front matter and learner-visible Markdown separately."""
    if not content.startswith("---\n"):
        return {}, content
    close = content.find("\n---\n", 4)
    if close < 0:
        fail("Unclosed lesson front matter")
        return {}, content
    return yaml.safe_load(content[4:close]) or {}, content[close + 5:]


def check_publication_consistency(syllabus, config):
    """Ensure every navigated lesson is published and learner-facing copy is clean."""
    records = {
        record["id"]: record
        for level in syllabus["levels"]
        for unit in level.get("units", [])
        for record in unit.get("lessons", [])
    }
    def gather(value):
        if isinstance(value, list):
            for item in value: yield from gather(item)
        elif isinstance(value, dict):
            for label, item in value.items():
                if isinstance(item, str):
                    yield label, item
                else:
                    yield from gather(item)
    navigated = dict(gather(config.get("nav", [])))
    visible_pages = {}
    for page in DOCS.rglob("lesson_*.md"):
        relative = page.relative_to(DOCS).as_posix()
        metadata, body = frontmatter_and_body(page.read_text(encoding="utf-8"))
        lesson_id = metadata.get("lesson_id")
        if not lesson_id or lesson_id not in records:
            fail(f"{relative}: unknown or missing lesson_id")
            continue
        record = records[lesson_id]
        if record["editorial_status"] != "published":
            fail(f"{relative}: present in public docs but curriculum status is {record['editorial_status']}")
        if metadata.get("editorial_status") != record["editorial_status"]:
            fail(f"{relative}: frontmatter and curriculum editorial_status differ")
        if metadata.get("content_version") != record.get("content_version"):
            fail(f"{relative}: frontmatter content_version differs from curriculum")
        if metadata.get("source_lesson") != record.get("source_lesson"):
            fail(f"{relative}: source_lesson differs from curriculum")
        if relative not in navigated.values():
            fail(f"{relative}: public lesson missing from navigation")
        for regex, reason in EDITORIAL_LEAKS:
            match = regex.search(body)
            if match:
                fail(f"{relative}: {reason}: {match.group(0)!r}")
        visible_pages[relative] = record
    for label, relative in gather(config.get("nav", [])):
        if re.search(r"\b(?:draft|in.review|not approved|pending publication)\b", label, re.I):
            fail(f"Navigation has an editorial label: {label}")
        if re.search(r"\blesson_[a-z]\.md$", relative) and relative not in visible_pages:
            fail(f"Navigation references unpublished/missing lesson: {relative}")
        if relative in visible_pages:
            expected = visible_pages[relative]["source_lesson"]
            if not label.startswith(expected + " — "):
                fail(f"Navigation label must start with original lesson code {expected}: {label}")
    # Audit all public prose, including indexes/home, for unequivocal stale publication notices.
    for page in DOCS.rglob("*.md"):
        if page.name.startswith("lesson_"):
            continue
        relative = page.relative_to(DOCS).as_posix()
        _, body = frontmatter_and_body(page.read_text(encoding="utf-8"))
        for regex, reason in EDITORIAL_LEAKS:
            match = regex.search(body)
            if match:
                fail(f"{relative}: {reason}: {match.group(0)!r}")
        if re.search(r"\b(?:full lessons.{0,80}not yet published|lesson pilot pending|partial source index)\b", body, re.I):
            fail(f"{relative}: stale public course-coverage statement")
    print(f"Checked {len(visible_pages)} published lesson metadata records and learner-visible pages")


def check_docs():
    config = load_yaml(ROOT / "mkdocs.yml")
    if config.get("docs_dir") != "docs":
        fail("Invalid docs_dir")
    nav = []
    def gather(value):
        if isinstance(value, list):
            for child in value:
                gather(child)
        elif isinstance(value, dict):
            for child in value.values():
                gather(child)
        elif isinstance(value, str):
            nav.append(value)
    gather(config.get("nav", []))
    for target in nav:
        if not (DOCS / target).is_file():
            fail(f"Missing MkDocs navigation target: {target}")
    pages = list(DOCS.rglob("*.md"))
    for page in pages:
        content = page.read_text(encoding="utf-8")
        for match in LINKS.finditer(content):
            target = local_target(page, match.group(2))
            if target and not (target.is_file() or (target.is_dir() and (target / "index.md").is_file())):
                fail(f"{page.relative_to(ROOT)}: broken local link {match.group(2)}")
        for match in IMAGES.finditer(content):
            if not match.group(1).strip():
                fail(f"{page.relative_to(ROOT)}: image missing alt")
            target = local_target(page, match.group(2))
            if target and not target.is_file():
                fail(f"{page.relative_to(ROOT)}: image missing {match.group(2)}")
        for match in HTML_IMAGES.finditer(content):
            if not HTML_ALT.search(match.group(0)):
                fail(f"{page.relative_to(ROOT)}: HTML image missing descriptive alt")
    check_publication_consistency(load_yaml(ROOT / "curriculum/master_syllabus.yaml"), config)
    print(f"Checked navigation and {len(pages)} Markdown documents")


if __name__ == "__main__":
    try:
        validate_curriculum()
        check_docs()
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, json.JSONDecodeError) as exc:
        fail(f"Uncaught validation error: {exc}")
    for item in ERRORS:
        print(f"ERROR: {item}", file=sys.stderr)
    if ERRORS:
        sys.exit(1)
    print("All course structure checks passed")
