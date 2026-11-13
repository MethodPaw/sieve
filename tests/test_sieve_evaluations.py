"""Fixture integrity only: these tests do not run or grade an AI model."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = ROOT / "evaluations/sieve"


class SieveEvaluationFixtureTests(unittest.TestCase):
    def setUp(self):
        self.suite = json.loads((SUITE_ROOT / "suite.json").read_text())

    def test_all_case_inputs_exist_and_stay_inside_suite(self):
        ids = [case["id"] for case in self.suite["cases"]]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        for case in self.suite["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["tools"], "none")
                self.assertTrue(case["attachments"])
                for relative in [case["prompt"], *case["attachments"]]:
                    path = (SUITE_ROOT / relative).resolve()
                    self.assertTrue(path.is_relative_to(SUITE_ROOT.resolve()))
                    self.assertTrue(path.is_file())
                    self.assertTrue(path.read_text().strip())
                criteria = case["criteria"]
                self.assertTrue(criteria)
                criterion_ids = [item["id"] for item in criteria]
                self.assertEqual(len(criterion_ids), len(set(criterion_ids)))
                self.assertTrue(all(item["pass_if"].strip() for item in criteria))

    def test_result_template_covers_every_criterion_without_claiming_runs(self):
        result = json.loads((SUITE_ROOT / "results/template.json").read_text())
        self.assertEqual(result["suite_version"], self.suite["suite_version"])
        self.assertIsNone(result["run_at"])
        self.assertIsNone(result["model"])
        self.assertEqual([c["id"] for c in result["cases"]],
                         [c["id"] for c in self.suite["cases"]])
        for case, recorded in zip(self.suite["cases"], result["cases"]):
            with self.subTest(case=case["id"]):
                self.assertEqual(recorded["status"], "not_run")
                self.assertIsNone(recorded["transcript"])
                self.assertEqual([c["id"] for c in recorded["criteria"]],
                                 [c["id"] for c in case["criteria"]])
                for criterion in recorded["criteria"]:
                    self.assertEqual(criterion["verdict"], "not_run")
                    self.assertIsNone(criterion["evidence"])
