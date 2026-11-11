"""Run fixed acceptance cases against a trusted local Python solution file."""

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = ROOT / "fixtures" / "cases.json"


def load_solution(path):
    """Import a local module exposing decide_withdrawal(payload)."""
    path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location("withdrawal_candidate", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load solution file: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, "decide_withdrawal", None)
    if not callable(function):
        raise ValueError("Solution must define callable decide_withdrawal(payload)")
    return function


def compare_output(expected, actual):
    """Compare required fixture fields; allow additional candidate diagnostics."""
    if not isinstance(actual, dict):
        return ["result must be a dictionary"]
    problems = []
    for key, expected_value in expected.items():
        if key not in actual:
            problems.append(f"missing required field {key!r}")
        elif actual[key] != expected_value:
            problems.append(f"{key}: expected {expected_value!r}, got {actual[key]!r}")
    return problems


def evaluate(solution_path, cases_path=DEFAULT_CASES):
    decide = load_solution(solution_path)
    cases = json.loads(Path(cases_path).read_text(encoding="utf-8"))
    results = []
    for case in cases:
        try:
            actual = decide(case["input"])
            problems = compare_output(case["expected"], actual)
        except Exception as exc:  # Candidate errors become a failed case, not a crash.
            problems = [f"raised {type(exc).__name__}: {exc}"]
        results.append({"id": case["id"], "passed": not problems, "problems": problems})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solution", required=True, help="Path to a trusted Python module to evaluate")
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="Optional path to a JSON fixture list")
    args = parser.parse_args(argv)
    try:
        results = evaluate(args.solution, args.cases)
    except Exception as exc:
        print(f"Evaluation could not start: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    for result in results:
        state = "PASS" if result["passed"] else "FAIL"
        print(f"{state} {result['id']}")
        for problem in result["problems"]:
            print(f"  - {problem}")
    passed = sum(result["passed"] for result in results)
    print(f"\nSummary: {passed}/{len(results)} cases passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
