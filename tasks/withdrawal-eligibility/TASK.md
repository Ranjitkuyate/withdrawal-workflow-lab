# Task: Make withdrawal decisions deterministic

## Scenario

A fictional plan workflow receives a participant's withdrawal request. The current starter function can approve requests that should be rejected because it overlooks pending holds, uses an incorrect age boundary, and treats hardship reasons too loosely.

Fix `decide_withdrawal(payload)` in `starter/withdrawal_rules.py`. Keep the public function name and return the decision object described below. You may refactor the implementation, but do not change the fixture contract or verifier.

## Input contract

The input is a JSON-compatible object with:

```json
{
  "account_balance": "1000.00",
  "pending_amount": "250.00",
  "participant_age": "59.5",
  "request": {
    "amount": "750.00",
    "hardship_reason": null,
    "documents_complete": false
  }
}
```

- All monetary values are decimal strings with at most two fractional digits.
- `account_balance` and `pending_amount` must be valid non-negative values; pending amount cannot exceed the balance.
- The request amount must be valid and strictly positive.
- The available balance is `account_balance - pending_amount`.
- A request cannot exceed the available balance. Equality is allowed.
- Age `59.5` or higher is age-eligible in this fictional exercise.
- Below `59.5`, approval requires an allowed hardship reason (`MEDICAL`, `HOUSING`, or `EDUCATION`) and `documents_complete` exactly `true`.
- Invalid or incomplete data must be denied, never silently treated as approval.

## Output contract

Return a dictionary containing these fields:

```json
{
  "decision": "APPROVE",
  "reason_code": "AGE_ELIGIBLE",
  "available_amount": "750.00",
  "requested_amount": "750.00"
}
```

Allowed decisions are `APPROVE` and `DENY`. Required reason codes are:

- `AGE_ELIGIBLE`
- `DOCUMENTED_HARDSHIP`
- `INVALID_ACCOUNT_DATA`
- `INVALID_AMOUNT`
- `INVALID_AGE`
- `INSUFFICIENT_AVAILABLE_BALANCE`
- `ELIGIBILITY_NOT_MET`
- `INVALID_HARDSHIP_REASON`
- `MISSING_HARDSHIP_DOCUMENTATION`

Amounts in the result use two decimal places. If the account values cannot be used to calculate an available balance, `available_amount` must be `null`. If the request amount cannot be parsed, `requested_amount` must be `null`. Additional result fields are allowed; the verifier checks the required fields only.

## Expected reasoning

Validate inputs before approving. Compute available funds after holds. Reject a request that exceeds that amount, but allow an exact match. Apply the age rule at the stated boundary. If the age rule does not apply, require both an allowed hardship reason and complete documentation. Prefer a specific denial code over a generic one so reviewers can understand the outcome.

## How to check a solution

From the repository root, run:

```bash
python3 verify.py --solution path/to/withdrawal_rules.py
```

The fixture set is in `fixtures/cases.json`. The verifier imports the supplied local Python file and executes it, so do not point it at untrusted code. This exercise is fictional and does not represent real financial or plan rules.
