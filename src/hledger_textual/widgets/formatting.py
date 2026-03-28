"""Shared formatting helpers for financial amounts."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from functools import lru_cache

from babel.numbers import format_decimal, get_decimal_symbol, get_group_symbol

# Matches left-side currency symbol amounts with 3+ decimal places.
# Handles both €-2442.140 (symbol before minus) and -€1.730 (minus before symbol).
_FMT_STR_RE = re.compile(r"^(-?)([€$£¥₿₹])(-?)([\d,]+\.\d{3,})$")


@lru_cache(maxsize=1)
def _number_locale() -> str:
    """Return the cached number locale from config."""
    from hledger_textual.config import load_number_locale
    return load_number_locale()


def fmt_amount_str(s: str) -> str:
    """Round a hledger amount string to 2 decimal places and apply locale formatting.

    Only affects amounts with a left-side currency symbol (€, $, etc.) that
    have more than 2 decimal places.  Named-commodity amounts (``164 XEON``,
    ``2.00 XDWD``), plain integers, and amounts already at ≤ 2 decimal places
    are returned unchanged.

    Handles both ``€-2442.140`` (symbol before minus) and ``-€1.730``
    (minus before symbol) formats.

    Args:
        s: Raw amount string, e.g. from hledger CSV output or ``Amount.format()``.

    Returns:
        Locale-formatted amount string with 2 decimal places, or the original
        string if it does not match a recognised currency format.
    """
    s = s.strip()
    m = _FMT_STR_RE.match(s)
    if not m:
        return s
    minus1, sym, minus2, numpart = m.groups()
    try:
        qty = Decimal(numpart.replace(",", "")).quantize(Decimal("0.01"))
        sign = Decimal(-1) if (minus1 or minus2) else Decimal(1)
        return fmt_amount(qty * sign, sym)
    except InvalidOperation:
        return s


def fmt_amount(qty: Decimal, commodity: str) -> str:
    """Format a decimal amount with its commodity symbol using the configured locale.

    Args:
        qty: The numeric quantity.
        commodity: The commodity symbol (e.g. ``'€'``, ``'EUR'``).

    Returns:
        A locale-formatted string like ``'€1.234,56'`` (it_IT) or
        ``'€1,234.56'`` (en_US), or just the formatted number if no commodity.
    """
    locale = _number_locale()
    formatted = format_decimal(qty, format="#,##0.00", locale=locale)
    if not commodity:
        return formatted
    if len(commodity) == 1:
        return f"{commodity}{formatted}"
    return f"{formatted} {commodity}"


def fmt_digits(qty: Decimal, commodity: str) -> str:
    """Format a decimal amount for the Textual Digits widget.

    The Digits widget only supports ``0-9``, ``.``, ``:``, ``-``, and space.
    This function formats using the configured locale but replaces the
    thousands separator with a space and the decimal separator with ``'.'``
    so the output is always safe for Digits to render.

    Args:
        qty: The numeric quantity.
        commodity: The commodity symbol (e.g. ``'€'``, ``'EUR'``).

    Returns:
        A Digits-safe string like ``'€1 234.56'`` or ``'0.00'`` if no commodity.
    """
    locale = _number_locale()
    thousands = get_group_symbol(locale)
    decimal_sep = get_decimal_symbol(locale)
    formatted = format_decimal(qty, format="#,##0.00", locale=locale)
    # Use a placeholder to avoid double-replacement when separators overlap
    result = formatted.replace(decimal_sep, "\x00")
    result = result.replace(thousands, " ")
    result = result.replace("\x00", ".")
    if not commodity:
        return result
    if len(commodity) == 1:
        return f"{commodity}{result}"
    return f"{result} {commodity}"


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
