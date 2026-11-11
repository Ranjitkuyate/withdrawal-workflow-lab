"""Golden reference for the fictional withdrawal-eligibility task."""

from decimal import Decimal, InvalidOperation

AGE_THRESHOLD = Decimal("59.5")
ALLOWED_HARDSHIP_REASONS = {"MEDICAL", "HOUSING", "EDUCATION"}


def _decimal_string(value, *, allow_zero=True):
    """Parse a non-negative decimal string with no more than two money digits."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError):
        return None
    if not number.is_finite() or number < 0:
        return None
    if number.as_tuple().exponent < -2:
        return None
    if not allow_zero and number <= 0:
        return None
    return number


def _format_money(value):
    return f"{value:.2f}" if value is not None else None


def _result(decision, reason_code, available, requested):
    return {
        "decision": decision,
        "reason_code": reason_code,
        "available_amount": _format_money(available),
        "requested_amount": _format_money(requested),
    }


def decide_withdrawal(payload):
    """Evaluate one request using only the fictional rules in TASK.md."""
    if not isinstance(payload, dict):
        return _result("DENY", "INVALID_ACCOUNT_DATA", None, None)

    balance = _decimal_string(payload.get("account_balance"))
    pending = _decimal_string(payload.get("pending_amount"))
    if balance is None or pending is None or pending > balance:
        return _result("DENY", "INVALID_ACCOUNT_DATA", None, None)
    available = balance - pending

    request = payload.get("request")
    if not isinstance(request, dict):
        return _result("DENY", "INVALID_AMOUNT", available, None)

    requested = _decimal_string(request.get("amount"), allow_zero=False)
    if requested is None:
        return _result("DENY", "INVALID_AMOUNT", available, None)
    if requested > available:
        return _result("DENY", "INSUFFICIENT_AVAILABLE_BALANCE", available, requested)

    age_value = payload.get("participant_age")
    if not isinstance(age_value, str) or not age_value.strip():
        return _result("DENY", "INVALID_AGE", available, requested)
    try:
        age = Decimal(age_value)
    except (InvalidOperation, ValueError):
        return _result("DENY", "INVALID_AGE", available, requested)
    if not age.is_finite() or age < 0:
        return _result("DENY", "INVALID_AGE", available, requested)

    if age >= AGE_THRESHOLD:
        return _result("APPROVE", "AGE_ELIGIBLE", available, requested)

    reason = request.get("hardship_reason")
    if reason is None or reason == "":
        return _result("DENY", "ELIGIBILITY_NOT_MET", available, requested)
    if not isinstance(reason, str) or reason.upper() not in ALLOWED_HARDSHIP_REASONS:
        return _result("DENY", "INVALID_HARDSHIP_REASON", available, requested)
    if request.get("documents_complete") is not True:
        return _result("DENY", "MISSING_HARDSHIP_DOCUMENTATION", available, requested)

    return _result("APPROVE", "DOCUMENTED_HARDSHIP", available, requested)
