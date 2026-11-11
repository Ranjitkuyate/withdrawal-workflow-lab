import json
from pathlib import Path
import tempfile
import unittest

from verify import compare_output, evaluate

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference" / "withdrawal_rules.py"
STARTER = ROOT / "tasks" / "withdrawal-eligibility" / "starter" / "withdrawal_rules.py"
CASES = ROOT / "fixtures" / "cases.json"


class VerifierTests(unittest.TestCase):
    def test_extra_diagnostic_fields_are_allowed(self):
        self.assertEqual(
            compare_output({"decision": "DENY"}, {"decision": "DENY", "debug": "useful"}),
            [],
        )

    def test_missing_or_wrong_contract_fields_are_reported(self):
        problems = compare_output(
            {"decision": "APPROVE", "reason_code": "AGE_ELIGIBLE"},
            {"decision": "DENY"},
        )
        self.assertEqual(len(problems), 2)
        self.assertIn("decision", problems[0])
        self.assertIn("reason_code", problems[1])

    def test_reference_passes_every_fixture(self):
        results = evaluate(REFERENCE, CASES)
        self.assertTrue(results)
        self.assertTrue(all(result["passed"] for result in results), results)

    def test_intentionally_buggy_starter_is_rejected(self):
        results = evaluate(STARTER, CASES)
        self.assertTrue(results)
        self.assertTrue(any(not result["passed"] for result in results))

    def test_candidate_exception_is_a_case_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            module = Path(temp) / "broken.py"
            module.write_text(
                "def decide_withdrawal(payload):\n    raise RuntimeError('intentional')\n",
                encoding="utf-8",
            )
            one_case = Path(temp) / "one.json"
            fixture = json.loads(CASES.read_text(encoding="utf-8"))[0]
            one_case.write_text(json.dumps([fixture]), encoding="utf-8")
            results = evaluate(module, one_case)
        self.assertFalse(results[0]["passed"])
        self.assertIn("RuntimeError", results[0]["problems"][0])


if __name__ == "__main__":
    unittest.main()
