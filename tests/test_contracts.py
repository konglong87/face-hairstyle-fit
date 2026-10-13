from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from scripts.contracts import (
    DEFAULT_CATALOG, ROOT, ContractError, load_catalog, read_json,
    validate_catalog, validate_report,
)
from scripts.rendering import render_html


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()
        self.data = read_json(DEFAULT_CATALOG)
        self.report = read_json(ROOT / "examples" / "provisional-report.json")

    def reject(self, report):
        with self.assertRaises(ContractError):
            validate_report(report, self.catalog)

    def test_starter_catalog(self):
        self.assertEqual(5, sum(s["kind"] == "family" for s in self.catalog.styles.values()))
        self.assertEqual(7, len(self.catalog.dimensions))

    def test_extension_does_not_need_code_change(self):
        new = deepcopy(self.data["styles"][0])
        new["id"] = "new-family"
        self.data["styles"].append(new)
        catalog = validate_catalog(self.data)
        self.report["recommendations"][0]["family_id"] = "new-family"
        validate_report(self.report, catalog)

    def test_duplicate_ids_rejected(self):
        self.data["styles"].append(deepcopy(self.data["styles"][0]))
        with self.assertRaises(ContractError):
            validate_catalog(self.data)

    def test_reversed_range_rejected(self):
        self.data["styles"][0]["ranges"]["linearity"] = [4, 1]
        with self.assertRaises(ContractError):
            validate_catalog(self.data)

    def test_incomplete_dimensions_rejected(self):
        del self.data["styles"][0]["ranges"]["linearity"]
        with self.assertRaises(ContractError):
            validate_catalog(self.data)

    def test_bad_recipe_reference_rejected(self):
        self.data["styles"][-1]["families"] = ["missing-family"]
        with self.assertRaises(ContractError):
            validate_catalog(self.data)

    def test_blank_catalog_definition_rejected(self):
        self.data["styles"][0]["definition"] = "   "
        with self.assertRaises(ContractError):
            validate_catalog(self.data)

    def test_example_passes(self):
        validate_report(self.report, self.catalog)

    def test_fake_probability_not_supported(self):
        self.report["recommendations"][0]["probability"] = 0.92
        self.reject(self.report)

    def test_missing_image_reference_rejected(self):
        self.report["observations"][0]["image_id"] = "absent"
        self.reject(self.report)

    def test_missing_evidence_rejected(self):
        self.report["recommendations"][0]["evidence_ids"] = ["absent"]
        self.reject(self.report)

    def test_unknown_role_cannot_be_ready(self):
        self.report["status"] = "ready"
        self.reject(self.report)

    def test_effect_only_cannot_be_personal_recommendation(self):
        self.report["images"][0]["role"] = "expected_effect"
        self.reject(self.report)

    def test_effect_face_evidence_rejected(self):
        self.report["images"][0]["role"] = "reference"
        self.report["observations"][0]["scope"] = "face"
        self.reject(self.report)

    def test_unknown_face_confidence_rejected(self):
        self.report["observations"][0].update(scope="face", confidence="high")
        self.reject(self.report)

    def test_multiple_faces_need_explicit_target(self):
        self.report["images"][0]["face_count"] = 2
        self.reject(self.report)
        self.report["images"][0]["target_selected"] = True
        validate_report(self.report, self.catalog)

    def test_blocked_photo_is_not_usable(self):
        for issue in ["blur", "occluded", "extreme_pose", "no_face"]:
            with self.subTest(issue=issue):
                report = deepcopy(self.report)
                report["images"][0]["issues"].append(issue)
                self.reject(report)

    def test_needs_input_has_no_personal_verdict(self):
        self.report["status"] = "needs_input"
        self.reject(self.report)
        self.report["recommendations"] = []
        self.report["experiments"] = []
        self.report["images"][0]["face_count"] = 0
        validate_report(self.report, self.catalog)

    def test_unresolved_needs_question(self):
        self.report["questions"] = []
        self.reject(self.report)

    def test_family_and_expression_not_interchangeable(self):
        self.report["recommendations"][0]["family_id"] = "korean"
        self.reject(self.report)

    def test_recipe_compatibility_checked(self):
        self.report["recommendations"][0]["recipe_id"] = "sweet-cool"
        self.reject(self.report)

    def test_modules_can_explicitly_skip(self):
        self.report["recommendations"][0]["plan"]["makeup"].update(
            status="skip", actions=[], reason="用户明确不化妆。")
        validate_report(self.report, self.catalog)

    def test_skip_cannot_smuggle_actions(self):
        self.report["recommendations"][0]["plan"]["makeup"]["status"] = "skip"
        self.reject(self.report)

    def test_propose_cannot_be_empty(self):
        self.report["recommendations"][0]["plan"]["hair"]["actions"] = []
        self.reject(self.report)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"id":"one","id":"two"}')
            with self.assertRaises(ContractError):
                read_json(path)

    def test_render_escapes_untrusted_content(self):
        self.report["summary"] = '<img src=x onerror="alert(1)">'
        self.report["recommendations"][0]["plan"]["hair"]["actions"] = ['<script>alert(1)</script>']
        output = render_html(self.report, self.catalog)
        self.assertNotIn("<script>", output)
        self.assertNotIn("<img src=x", output)
        self.assertIn("&lt;img", output)
        self.assertIn("Content-Security-Policy", output)


if __name__ == "__main__":
    unittest.main()
