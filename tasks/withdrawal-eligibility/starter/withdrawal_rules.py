"""Intentionally flawed starting point for the withdrawal eligibility task."""


def decide_withdrawal(payload):
    """Return a withdrawal decision. Repair the intentional rule defects."""
    account_balance = float(payload.get("account_balance", 0))
    amount = float(payload.get("request", {}).get("amount", 0))
    age = float(payload.get("participant_age", 0))
    request = payload.get("request", {})

    # Intentional defects for the task:
    # - ignores pending holds when computing available balance
    # - uses 59 instead of the stated 59.5 threshold
    # - accepts any non-empty hardship reason without requiring documents
    if amount > 0 and amount <= account_balance and (age >= 59 or request.get("hardship_reason")):
        return {
            "decision": "APPROVE",
            "reason_code": "APPROVED",
            "available_amount": f"{account_balance:.2f}",
            "requested_amount": f"{amount:.2f}",
        }

    return {
        "decision": "DENY",
        "reason_code": "DENIED",
        "available_amount": f"{account_balance:.2f}",
        "requested_amount": f"{amount:.2f}",
    }
