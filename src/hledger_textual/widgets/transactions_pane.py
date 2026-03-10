"""Transactions list pane widget (full CRUD)."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget

from hledger_textual.hledger import HledgerError, load_period_summary
from hledger_textual.models import Transaction, TransactionStatus
from hledger_textual.widgets.period_summary_cards import PeriodSummaryCards
from hledger_textual.widgets.transactions_table import TransactionsTable


class TransactionsPane(Widget):
    """Widget showing all transactions with add / edit / delete actions.

    Composes a :class:`~hledger_textual.widgets.transactions_table.TransactionsTable`
    for the shared filter bar and DataTable, and adds journal-mutation bindings
    on top.  Compact summary cards above the table show the current month's
    Income / Expenses / Net and update when the user navigates months.
    """

    BINDINGS = [
        Binding("a", "add", "Add", show=True, priority=True),
        Binding("e", "edit", "Edit", show=True, priority=True),
        Binding("enter", "edit", "Edit", show=False),
        Binding("d", "delete", "Delete", show=True, priority=True),
        Binding("c", "clone", "Clone", show=True, priority=True),
        Binding("m", "move", "Move", show=True, priority=True),
        Binding("slash", "filter", "Search", show=True, priority=True),
        Binding("f", "saved_filters", "Filters", show=True, priority=True),
        Binding("s", "save_filter", "Save Filter", show=True, priority=True),
        Binding("r", "refresh", "Refresh", show=True, priority=True),
        Binding("escape", "dismiss_filter", "Dismiss filter", show=False),
        Binding("left", "prev_month", "Previous month", show=False, priority=True),
        Binding("right", "next_month", "Next month", show=False, priority=True),
        Binding("t", "today_month", "Today", show=False, priority=True),
        Binding("*", "toggle_cleared", "Toggle cleared", show=False, priority=True),
        Binding(
            "exclamation_mark",
            "toggle_pending",
            "Toggle pending",
            show=False,
            priority=True,
        ),
    ]

    def __init__(self, journal_file: Path, **kwargs) -> None:
        """Initialise the pane.

        Args:
            journal_file: Path to the hledger journal file.
        """
        super().__init__(**kwargs)
        self.journal_file = journal_file

    def compose(self) -> ComposeResult:
        """Render compact summary cards and the shared transactions table."""
        yield PeriodSummaryCards(compact=True, id="txn-summary-cards")
        yield TransactionsTable(self.journal_file)

    def on_mount(self) -> None:
        """Load the summary for the initial month."""
        self._load_summary(self._table.current_month)

    def on_show(self) -> None:
        """Re-focus the table when the pane becomes visible."""
        self.query_one(TransactionsTable).on_show()

    @property
    def _table(self) -> TransactionsTable:
        return self.query_one(TransactionsTable)

    # ------------------------------------------------------------------
    # Month-change handler
    # ------------------------------------------------------------------

    def on_transactions_table_month_changed(
        self, event: TransactionsTable.MonthChanged
    ) -> None:
        """Reload summary cards when the displayed month changes."""
        self._load_summary(event.month)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def reload(self) -> None:
        """Silently reload transactions and summary (no notification)."""
        self._table.reload()
        self._load_summary(self._table.current_month)

    def action_refresh(self) -> None:
        """Reload transactions and summary from the journal."""
        self._table.do_refresh()
        self._load_summary(self._table.current_month)

    def action_filter(self) -> None:
        """Show the filter panel."""
        self._table.show_filter()

    def action_dismiss_filter(self) -> None:
        """Hide the search bar and reset all filters."""
        self._table.dismiss_filter()

    def action_saved_filters(self) -> None:
        """Open the saved filters modal to browse and apply filters."""
        from hledger_textual.screens.saved_filters import SavedFiltersModal

        def on_select(query: str | None) -> None:
            if query:
                self._table.apply_saved_filter(query)

        self.app.push_screen(SavedFiltersModal(), callback=on_select)

    def action_save_filter(self) -> None:
        """Save the current search filter with a user-chosen name."""
        from hledger_textual.screens.saved_filters import SavedFiltersModal

        query = self._table.current_search_query
        if not query:
            self.notify("No active filter to save", severity="warning", timeout=3)
            return
        self.app.push_screen(SavedFiltersModal(current_query=query))

    def action_prev_month(self) -> None:
        """Navigate to the previous month."""
        self._table.prev_month()

    def action_next_month(self) -> None:
        """Navigate to the next month."""
        self._table.next_month()

    def action_today_month(self) -> None:
        """Jump to the current month."""
        self._table.today_month()

    def action_add(self) -> None:
        """Open the form to add a new transaction."""
        from hledger_textual.screens.transaction_form import TransactionFormScreen

        def on_save(result: Transaction | None) -> None:
            if result is not None:
                self._do_append(result)

        self.app.push_screen(
            TransactionFormScreen(journal_file=self.journal_file),
            callback=on_save,
        )

    def action_edit(self) -> None:
        """Open the form to edit the selected transaction."""
        self._table.do_edit()

    def action_delete(self) -> None:
        """Delete the selected transaction (with confirmation)."""
        self._table.do_delete()

    def action_toggle_cleared(self) -> None:
        """Toggle the cleared status of the selected transaction."""
        self._table.do_toggle_status(TransactionStatus.CLEARED)

    def action_toggle_pending(self) -> None:
        """Toggle the pending status of the selected transaction."""
        self._table.do_toggle_status(TransactionStatus.PENDING)

    def action_clone(self) -> None:
        """Clone the selected transaction with an empty date for the user to fill."""
        import dataclasses

        from hledger_textual.screens.transaction_form import TransactionFormScreen

        txn = self._table.get_selected_transaction()
        if txn is None:
            self.notify("No transaction selected", severity="warning", timeout=3)
            return

        clone = dataclasses.replace(txn, date="", index=0)

        def on_save(result: Transaction | None) -> None:
            if result is not None:
                self._do_append(result)

        self.app.push_screen(
            TransactionFormScreen(
                journal_file=self.journal_file,
                transaction=clone,
                clone=True,
            ),
            callback=on_save,
        )

    def action_move(self) -> None:
        """Show the move dialog to change the transaction date."""
        from hledger_textual.screens.move_confirm import MoveConfirmModal

        txn = self._table.get_selected_transaction()
        if txn is None:
            self.notify("No transaction selected", severity="warning", timeout=3)
            return

        def on_confirm(new_date: str | None) -> None:
            if new_date is not None:
                self._table.do_move_to_date(txn, new_date)

        self.app.push_screen(MoveConfirmModal(txn), callback=on_confirm)

    # ------------------------------------------------------------------
    # Summary loading
    # ------------------------------------------------------------------

    @work(thread=True, exclusive=True, group="txn-summary")
    def _load_summary(self, month: date) -> None:
        """Load the period summary for *month* in a background thread.

        When *month* is the current calendar month the date range is capped at
        today so that scheduled (future) transactions do not inflate the totals.
        """
        today = date.today()
        if month.year == today.year and month.month == today.month:
            end = today + timedelta(days=1)
            period = f"{month.isoformat()}..{end.isoformat()}"
        else:
            period = month.strftime("%Y-%m")
        try:
            summary = load_period_summary(self.journal_file, period)
        except HledgerError:
            summary = None

        self.app.call_from_thread(
            self.query_one(PeriodSummaryCards).update_summary, summary
        )

    # ------------------------------------------------------------------
    # Mutation helpers (add is local — only needed in the main view)
    # ------------------------------------------------------------------

    @work(thread=True)
    def _do_append(self, transaction: Transaction) -> None:
        """Append a transaction to the journal and emit JournalChanged."""
        from hledger_textual.journal import JournalError, append_transaction

        try:
            append_transaction(self.journal_file, transaction)
            self.app.call_from_thread(self.notify, "Transaction added", timeout=3)
            self.app.call_from_thread(
                self._table.post_message, TransactionsTable.JournalChanged()
            )
        except JournalError as exc:
            self.app.call_from_thread(
                self.notify, str(exc), severity="error", timeout=8
            )
