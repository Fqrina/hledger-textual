"""Integration tests for the Transactions pane."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from hledger_textual.app import HledgerTuiApp
from hledger_textual.widgets.transactions_table import TransactionsTable
from tests.conftest import has_hledger

pytestmark = pytest.mark.skipif(not has_hledger(), reason="hledger not installed")


@pytest.fixture
def txn_pane_journal(tmp_path: Path) -> Path:
    """A minimal journal with current-month transactions."""
    today = date.today()
    d1 = today.replace(day=1)
    d2 = today.replace(day=2)
    content = (
        f"{d1.isoformat()} * Grocery shopping\n"
        "    expenses:food              €40.80\n"
        "    assets:bank:checking\n"
        "\n"
        f"{d2.isoformat()} Salary\n"
        "    assets:bank:checking     €3000.00\n"
        "    income:salary\n"
    )
    journal = tmp_path / "test.journal"
    journal.write_text(content)
    return journal


@pytest.fixture
def txn_app(txn_pane_journal: Path) -> HledgerTuiApp:
    """Create an app instance for transactions pane testing."""
    return HledgerTuiApp(journal_file=txn_pane_journal)


class TestTodayMonth:
    """Tests for the 't' (today month) keybinding in TransactionsPane."""

    async def test_today_resets_to_current_month(self, txn_app: HledgerTuiApp):
        """Pressing 't' after navigating away returns to the current month."""
        async with txn_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("2")  # switch to transactions tab
            await pilot.pause(delay=1.0)

            txn_table = txn_app.screen.query_one(TransactionsTable)
            original_month = txn_table.current_month

            # Navigate to previous month
            await pilot.press("left")
            await pilot.pause(delay=1.0)
            assert txn_table.current_month < original_month

            # Press 't' to jump back to today
            await pilot.press("t")
            await pilot.pause(delay=1.0)
            assert txn_table.current_month == date.today().replace(day=1)

    async def test_today_updates_period_label(self, txn_app: HledgerTuiApp):
        """Pressing 't' updates the period label to the current month name."""
        from textual.widgets import Static

        async with txn_app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("2")
            await pilot.pause(delay=1.0)

            # Navigate away
            await pilot.press("left")
            await pilot.pause(delay=1.0)

            # Press 't' to jump back
            await pilot.press("t")
            await pilot.pause(delay=1.0)

            label = txn_app.screen.query_one("#txn-period-label", Static)
            expected = date.today().replace(day=1).strftime("%B %Y")
            assert str(label.renderable) == expected
