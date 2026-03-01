"""Date arithmetic utilities."""

from __future__ import annotations

from datetime import date


def prev_month(d: date) -> date:
    """Return the first day of the month before *d*.

    Args:
        d: A date whose month to decrement.

    Returns:
        A new date set to the first of the previous month.
    """
    month, year = d.month - 1, d.year
    if month < 1:
        month, year = 12, year - 1
    return d.replace(year=year, month=month, day=1)


def next_month(d: date) -> date:
    """Return the first day of the month after *d*.

    Args:
        d: A date whose month to increment.

    Returns:
        A new date set to the first of the next month.
    """
    month, year = d.month + 1, d.year
    if month > 12:
        month, year = 1, year + 1
    return d.replace(year=year, month=month, day=1)
