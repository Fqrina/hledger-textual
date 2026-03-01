"""Reusable Income / Expenses / Net summary cards widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Digits, Static

from hledger_textual.models import PeriodSummary
from hledger_textual.widgets.formatting import (
    compute_saving_rate,
    fmt_amount,
    fmt_digits,
)


class PeriodSummaryCards(Widget):
    """Three side-by-side cards showing Income, Expenses, and Net for a period.

    Args:
        compact: When True, applies the ``compact-cards`` CSS class which hides
            auxiliary text (net note, saving rate) for use in tighter layouts.
    """

    def __init__(self, compact: bool = False, **kwargs) -> None:
        """Initialize the cards widget.

        Args:
            compact: Whether to use the compact layout variant.
        """
        super().__init__(**kwargs)
        self._compact = compact

    def compose(self) -> ComposeResult:
        """Yield three summary cards inside a horizontal container."""
        classes = "period-summary-cards"
        if self._compact:
            classes += " compact-cards"
        with Horizontal(classes=classes):
            with Vertical(classes="summary-card"):
                yield Static("Income", classes="summary-card-title")
                yield Digits("--", classes="summary-card-value income-value")
            with Vertical(classes="summary-card"):
                yield Static("Expenses", classes="summary-card-title")
                yield Digits("--", classes="summary-card-value expenses-value")
            with Vertical(classes="summary-card"):
                yield Static("Net", classes="summary-card-title")
                yield Digits("--", classes="summary-card-value net-value")
                yield Static("", classes="net-note")
                yield Static("", classes="saving-rate")

    def update_summary(self, summary: PeriodSummary | None) -> None:
        """Update all card values from a PeriodSummary.

        Args:
            summary: The period data to display, or None to reset to dashes.
        """
        if summary is not None:
            com = summary.commodity
            income_text = fmt_digits(summary.income, com)
            expense_text = fmt_digits(summary.expenses, com)
            net = summary.net
            net_text = fmt_digits(abs(net), com)

            self.query_one(".income-value", Digits).update(income_text)
            self.query_one(".expenses-value", Digits).update(expense_text)

            net_widget = self.query_one(".net-value", Digits)
            if net >= 0:
                net_widget.update(net_text)
                net_widget.remove_class("net-negative")
                net_widget.add_class("net-positive")
            else:
                net_widget.update(f"-{net_text}")
                net_widget.remove_class("net-positive")
                net_widget.add_class("net-negative")

            note = self.query_one(".net-note", Static)
            if summary.investments > 0:
                inv_text = fmt_amount(summary.investments, com)
                note.update(f"incl. {inv_text} invested")
                note.display = True
            else:
                note.update("")
                note.display = False

            rate_widget = self.query_one(".saving-rate", Static)
            rate = compute_saving_rate(summary.income, summary.expenses)
            if rate is not None:
                rate_widget.update(f"Saving rate: {rate:.0f}%")
            else:
                rate_widget.update("")
        else:
            for cls in (".income-value", ".expenses-value", ".net-value"):
                self.query_one(cls, Digits).update("--")
            note = self.query_one(".net-note", Static)
            note.update("")
            note.display = False
            self.query_one(".saving-rate", Static).update("")
