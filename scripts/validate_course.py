#!/usr/bin/env python3
"""Validate curriculum metadata, MkDocs navigation, local links and image alt text."""
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
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ALT = re.compile(r"\balt\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE)
ERRORS = []


def error(message):
    ERRORS.append(message)


def check_curriculum():
    with (ROOT / "curriculum/master_syllabus.yaml").open(encoding="utf-8") as fh:
        syllabus = yaml.safe_load(fh)
    with (ROOT / "curriculum/lesson_metadata.schema.json").open(encoding="utf-8") as fh:
        schema = json.load(fh)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    levels = syllabus.get("levels", [])
    if len(levels) != 7 or len({level["id"] for level in levels}) != 7:
        error("Expected seven distinct editorial levels")
    if set(syllabus.get("assessment", {}).get("skills", [])) != SKILLS:
        error("The six-skill set has changed")
    elementary = next((x for x in levels if x.get("id") == "elementary"), None)
    if elementary is None or [u["number"] for u in elementary["units"]] != list(range(1, 13)):
        error("Elementary must retain its twelve ordered units")
        return
    if elementary.get("lessons_per_unit") != ["A", "B", "C"]:
        error("Elementary must declare A/B/C lessons")
    first = elementary["units"][0]
    records = first.get("lessons", [])
    expected = {f"elementary.unit_01.lesson_{letter.lower()}" for letter in "ABC"}
    if {r.get("id") for r in records} != expected or len(records) != 3:
        error("Unit 1 must have exactly the distinct 1A, 1B and 1C records")
    for item in records:
        for issue in validator.iter_errors(item):
            error(f"{item.get('id', '?')}: {issue.message}")
        if item.get("source_verification") == "pending_original_index":
            if item.get("grammar") or item.get("vocabulary"):
                error(f"{item['id']}: no specific topics before original TOC verification")
            if item.get("editorial_status") not in {"planning_pending_source"}:
                error(f"{item['id']}: cannot advance editorial status without source check")
        if item.get("source_verification") == "source_index_confirmed" and not (item.get("grammar") and item.get("vocabulary")):
            error(f"{item['id']}: confirmed lesson needs assigned source topics")
        cefr = item.get("cefr", {})
        if cefr.get("alignment") == "descriptor_verified" and not cefr.get("descriptor_reference"):
            error(f"{item['id']}: verified CEFR mapping needs descriptor reference")
        if cefr.get("alignment") != "descriptor_verified" and cefr.get("descriptor_reference"):
            error(f"{item['id']}: provisional CEFR mapping cannot cite an unverified descriptor")
        oral = {x.get("skill") for x in item.get("oral_activities", [])}
        if oral != {"speaking", "listening", "pronunciation"}:
            error(f"{item['id']}: missing oral skill handoff")
        for prerequisite in item.get("prerequisites", []):
            if prerequisite not in expected:
                error(f"{item['id']}: unknown Unit 1 prerequisite: {prerequisite}")
    print("Curriculum and lesson metadata checked")


def resolve_local(path, target):
    target = unquote(urlsplit(target.strip().split(" ", 1)[0]).path)
    if not target or target.startswith(("#", "mailto:", "tel:")):
        return None
    parsed = urlsplit(target.strip())
    if parsed.scheme or target.startswith("//"):
        return None
    if target.startswith("/"):
        return DOCS / target.lstrip("/")
    return path.parent / target


def check_docs():
    with (ROOT / "mkdocs.yml").open(encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    if config.get("docs_dir") != "docs":
        error("Unexpected MkDocs docs_dir")
    nav_paths = []

    def walk(obj):
        if isinstance(obj, list):
            for x in obj:
                walk(x)
        elif isinstance(obj, dict):
            for x in obj.values():
                walk(x)
        elif isinstance(obj, str):
            nav_paths.append(obj)

    walk(config.get("nav", []))
    for relative in nav_paths:
        if not (DOCS / relative).is_file():
            error(f"Navigation target missing: {relative}")
    for path in DOCS.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        for match in LINK.finditer(content):
            candidate = resolve_local(path, match.group(1))
            if candidate and not (candidate.is_file() or (candidate.is_dir() and (candidate / "index.md").is_file())):
                error(f"{path.relative_to(ROOT)}: broken link {match.group(1)}")
        for match in IMAGE.finditer(content):
            if not match.group(1).strip():
                error(f"{path.relative_to(ROOT)}: image missing descriptive alt text")
            candidate = resolve_local(path, match.group(2))
            if candidate and not candidate.is_file():
                error(f"{path.relative_to(ROOT)}: missing image {match.group(2)}")
        for match in HTML_IMAGE.finditer(content):
            if not ALT.search(match.group()):
                error(f"{path.relative_to(ROOT)}: HTML image missing alt")
    print(f"MkDocs navigation and {len(list(DOCS.rglob('*.md')))} Markdown files checked")


if __name__ == "__main__":
    try:
        check_curriculum()
        check_docs()
    except (KeyError, TypeError, ValueError, yaml.YAMLError, OSError, json.JSONDecodeError) as exc:
        error(f"Validation aborted: {exc}")
    for failure in ERRORS:
        print(f"ERROR: {failure}", file=sys.stderr)
    if ERRORS:
        sys.exit(1)
    print("All course checks passed")
