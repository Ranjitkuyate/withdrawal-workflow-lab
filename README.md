# Withdrawal Workflow Lab

A personal practice project by Ranjit Kuyate: a deterministic Python coding-task lab built around a fictional withdrawal workflow. It gives a candidate a deliberately flawed starter, a precise task contract, fixed test cases, a reference solution, and a verifier.

I created this as a portfolio exercise to practice turning workflow requirements into testable rules, checking edge cases, and making expected outcomes reproducible. AI assistance was used during preparation. Review the code and tests carefully, and only describe design decisions you can explain. This is not code from an employer or client, not a production service, and not financial, tax, or plan-administration advice. All rules below are invented for this demo.

## What it demonstrates

- A realistic-but-fictional bug-fix task with a deliberately flawed starter implementation.
- A small reference solution with explicit input validation and deterministic decisions.
- A verifier that checks a candidate implementation against fixed JSON cases and reports each result.
- Boundary and negative cases for age eligibility, pending holds, amounts, hardship reasons, and documentation.
- Standard-library-only tests; no network access or third-party packages are needed.

## Run it

Requires Python 3.10 or newer. From this directory:

```bash
python3 -m unittest discover -s tests -v
python3 verify.py --solution reference/withdrawal_rules.py
```

The reference run should pass all cases. To see the intentionally defective starter fail the same checks:

```bash
python3 verify.py --solution tasks/withdrawal-eligibility/starter/withdrawal_rules.py
```

To try the task, copy the starter file, fix its `decide_withdrawal(payload)` function to meet the contract in [`tasks/withdrawal-eligibility/TASK.md`](tasks/withdrawal-eligibility/TASK.md), then point `verify.py` at your candidate file:

```bash
cp tasks/withdrawal-eligibility/starter/withdrawal_rules.py /tmp/my_withdrawal_rules.py
# Edit /tmp/my_withdrawal_rules.py, then:
python3 verify.py --solution /tmp/my_withdrawal_rules.py
```

## Rules in this exercise

A request is approved if it is positive, does not exceed the account balance after pending holds, and either meets the fictional age threshold (59.5) or is a documented hardship request with an allowed reason (`MEDICAL`, `HOUSING`, or `EDUCATION`). The exact rules and rejection codes are documented in the task file. Money values are decimal strings with up to two decimal places to avoid floating-point ambiguity.

| Case | Expected result |
| --- | --- |
| Age-eligible request at the exact available balance | `APPROVE / AGE_ELIGIBLE` |
| Age is exactly 59.5 | `APPROVE / AGE_ELIGIBLE` |
| Request is one cent above balance after a pending hold | `DENY / INSUFFICIENT_AVAILABLE_BALANCE` |
| Under-age request with an allowed, documented hardship | `APPROVE / DOCUMENTED_HARDSHIP` |
| Missing hardship documentation or an unknown reason | Denied with a specific reason code |
| Zero/negative amount or invalid account data | Denied deterministically |

## Project layout

- `tasks/withdrawal-eligibility/TASK.md` — problem statement and output contract.
- `tasks/withdrawal-eligibility/starter/withdrawal_rules.py` — deliberately buggy task input.
- `reference/withdrawal_rules.py` — golden reference implementation.
- `fixtures/cases.json` — named inputs and expected outputs used by the verifier.
- `verify.py` — loads a candidate module, runs the fixed cases, and checks contract fields.
- `tests/` — unit tests for the verifier and reference behavior.

## Verifier limitations

This is a local educational harness, not a secure code-execution sandbox. `verify.py` imports and runs the Python file supplied with `--solution`; only use code you trust. The verifier compares required contract fields and allows additional output fields, so a candidate may include useful diagnostics without failing solely for having extra keys. Passing the fixed cases is evidence only for these cases, not proof of correctness for every possible input.

## Short project explanation

> This is a compact, AI-assisted Python coding-task example based on a fictional withdrawal workflow. It pairs an intentionally flawed starter with a deterministic reference solution, named fixtures, and a verifier that checks exact-boundary and negative cases. The QA idea is to make the acceptance contract explicit and repeatable, while keeping the task small enough to inspect and explain.
