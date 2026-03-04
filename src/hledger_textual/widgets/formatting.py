"""Shared formatting helpers for financial amounts."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

# Matches left-side currency symbol amounts with 3+ decimal places.
# Handles both €-2442.140 (symbol before minus) and -€1.730 (minus before symbol).
_FMT_STR_RE = re.compile(r"^(-?)([€$£¥₿₹])(-?)([\d,]+\.\d{3,})$")


def fmt_amount_str(s: str) -> str:
    """Round a hledger amount string to 2 decimal places for display.

    Only affects amounts with a left-side currency symbol (€, $, etc.) that
    have more than 2 decimal places.  Named-commodity amounts (``164 XEON``,
    ``2.00 XDWD``), plain integers, and amounts already at ≤ 2 decimal places
    are returned unchanged.

    Handles both ``€-2442.140`` (symbol before minus) and ``-€1.730``
    (minus before symbol) formats.

    Args:
        s: Raw amount string, e.g. from hledger CSV output or ``Amount.format()``.

    Returns:
        Amount string with at most 2 decimal places, or the original string
        if it does not match a recognized currency format.
    """
    s = s.strip()
    m = _FMT_STR_RE.match(s)
    if not m:
        return s
    minus1, sym, minus2, numpart = m.groups()
    try:
        rounded = Decimal(numpart.replace(",", "")).quantize(Decimal("0.01"))
        return f"{minus1}{sym}{minus2}{rounded}"
    except InvalidOperation:
        return s


def fmt_amount(qty: Decimal, commodity: str) -> str:
    """Format a decimal amount with its commodity symbol.

    Args:
        qty: The numeric quantity.
        commodity: The commodity symbol (e.g. '\u20ac', 'EUR').

    Returns:
        A formatted string like '\u20ac1,234.56' or '0.00' if no commodity.
    """
    if not commodity:
        return f"{qty:,.2f}"
    # Left-side single-char commodities (symbols like \u20ac, $, \u00a3)
    if len(commodity) == 1:
        return f"{commodity}{qty:,.2f}"
    return f"{qty:,.2f} {commodity}"


def fmt_digits(qty: Decimal, commodity: str) -> str:
    """Format a decimal amount for the Digits widget.

    Like fmt_amount but uses spaces as thousands separator instead of commas,
    since the Digits widget does not support comma characters.

    Args:
        qty: The numeric quantity.
        commodity: The commodity symbol (e.g. '\u20ac', 'EUR').

    Returns:
        A formatted string like '\u20ac1 234.56' or '0.00' if no commodity.
    """
    return fmt_amount(qty, commodity).replace(",", "")


def compute_saving_rate(income: Decimal, expenses: Decimal) -> float | None:
    """Compute the saving rate as a percentage of income.

    Saving rate = (income - expenses) / income * 100.
    Investments count as savings (they are not included in expenses).

    Args:
        income: Total income for the period.
        expenses: Total expenses for the period (excluding investments).

    Returns:
        The saving rate percentage, or None if income is zero.
    """
    if income <= 0:
        return None
    return float((income - expenses) / income * 100)
