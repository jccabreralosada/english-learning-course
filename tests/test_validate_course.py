"""Regression tests for the reusable curriculum quality gates."""
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_course", ROOT / "scripts/validate_course.py")
course = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(course)
SCHEMA = json.loads((ROOT / "curriculum/lesson_metadata.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


class TestCourseValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        syllabus = course.load_yaml(ROOT / "curriculum/master_syllabus.yaml")
        cls.record = syllabus["levels"][0]["units"][0]["lessons"][0]

    def test_current_lesson_record_is_valid(self):
        self.assertFalse(list(VALIDATOR.iter_errors(self.record)))

    def test_missing_writing_outcome_is_rejected(self):
        candidate = self.record.copy()
        candidate.pop("writing_outcome")
        self.assertTrue(list(VALIDATOR.iter_errors(candidate)))

    def test_missing_provenance_is_rejected(self):
        candidate = {**self.record, "source_references": []}
        self.assertTrue(list(VALIDATOR.iter_errors(candidate)))

    def test_unverified_lesson_cannot_claim_topics(self):
        candidate = {**self.record, "source_verification": "pending_original_index"}
        self.assertTrue(list(VALIDATOR.iter_errors(candidate)))

    def test_original_index_provenance_has_private_fingerprint(self):
        references = self.record["source_references"]
        self.assertEqual(self.record["source_verification"], "source_index_confirmed")
        self.assertTrue(any(x.get("type") == "user_supplied_index" and
                            x.get("verified_against_user_image") and
                            len(x.get("asset_sha256", "")) == 64 for x in references))
        self.assertFalse(list(VALIDATOR.iter_errors(self.record)))

    def test_original_index_without_private_reference_is_rejected(self):
        candidate = {**self.record, "source_references": [{
            "type": "published_sample_index",
            "title": "External backup index",
            "url": "https://example.org/reference",
            "scope": "Contents 1A",
            "verified_against_user_image": False
        }]}
        self.assertTrue(list(VALIDATOR.iter_errors(candidate)))

    def test_original_index_requires_source_pronunciation(self):
        candidate = {**self.record, "source_pronunciation": [
            {"name": "word stress", "origin": "source_index_confirmed"}
        ]}
        self.assertFalse(list(VALIDATOR.iter_errors(candidate)))

    def test_invalid_editorial_status_is_rejected(self):
        candidate = {**self.record, "editorial_status": "mastered"}
        self.assertTrue(list(VALIDATOR.iter_errors(candidate)))

    def test_published_1a_and_1b_metadata_match_curriculum(self):
        syllabus = course.load_yaml(ROOT / "curriculum/master_syllabus.yaml")
        records = {x["id"]: x for x in syllabus["levels"][0]["units"][0]["lessons"]}
        for code in "ab":
            page = ROOT / f"docs/elementary/unit_01/lesson_{code}.md"
            front, body = course.frontmatter_and_body(page.read_text(encoding="utf-8"))
            self.assertEqual(front["editorial_status"], "published")
            self.assertEqual(front["editorial_status"], records[front["lesson_id"]]["editorial_status"])
            self.assertFalse(any(regex.search(body) for regex, _ in course.EDITORIAL_LEAKS))
        self.assertEqual(records["elementary.unit_01.lesson_c"]["editorial_status"], "planning_pending_source")

    def test_editorial_leak_patterns_are_precise(self):
        disallowed = [
            "Editorial draft — not approved", "Available on development branch",
            "This lesson is not yet published", "See Pull Request #17",
            "source copy: elementary_1.png", "Lesson ID: elementary.unit_01.lesson_a"
        ]
        allowed = [
            "Review the grammar and practise the questions.",
            "This is an ungraded assessment practice activity.",
            "Check the review section after completing the exercises.",
            "You can repeat the pronunciation exercise.",
            "An original learning program based on published research."
        ]
        for value in disallowed:
            self.assertTrue(any(regex.search(value) for regex, _ in course.EDITORIAL_LEAKS), value)
        for value in allowed:
            self.assertFalse(any(regex.search(value) for regex, _ in course.EDITORIAL_LEAKS), value)

    def test_frontmatter_is_separate_from_student_copy(self):
        text = "---\\neditorial_status: published\\nlesson_id: test.id\\n---\\n# Lesson\\nReview the examples."
        front, body = course.frontmatter_and_body(text.replace("\\\\n", "\\n"))
        self.assertEqual(front["editorial_status"], "published")
        self.assertNotIn("editorial_status", body)
        self.assertIn("Review the examples.", body)

    def test_external_link_is_not_local(self):
        self.assertIsNone(course.local_target(ROOT / "docs/index.md", "https://example.org/external"))

    def test_local_link_resolves(self):
        target = course.local_target(ROOT / "docs/index.md", "elementary/index.md")
        self.assertTrue(target.is_file())


if __name__ == "__main__":
    unittest.main()
