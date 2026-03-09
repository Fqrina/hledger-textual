"""Preview modal for generating recurring transactions."""

from __future__ import annotations

from datetime import date

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, Static

from hledger_textual.models import RecurringRule


class RecurringGenerateScreen(ModalScreen[bool]):
    """A modal showing a preview of pending recurring transactions to generate."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, pending: list[tuple[RecurringRule, list[date]]]) -> None:
        """Initialize the modal.

        Args:
            pending: List of (rule, dates) pairs representing transactions to generate.
        """
        super().__init__()
        self.pending = pending

    @property
    def _total_count(self) -> int:
        """Return the total number of transactions to generate."""
        return sum(len(dates) for _, dates in self.pending)

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        total = self._total_count
        summary = f"{total} transaction{'s' if total != 1 else ''} to generate"

        with Vertical(id="recurring-generate-dialog"):
            yield Label("Generate Recurring Transactions", id="recurring-generate-title")
            yield Static(summary, id="recurring-generate-summary")
            yield DataTable(id="recurring-generate-table")
            with Horizontal(id="recurring-generate-buttons"):
                yield Button("Cancel", variant="default", id="btn-recurring-gen-cancel")
                yield Button(
                    "Generate All", variant="success", id="btn-recurring-generate"
                )

    def on_mount(self) -> None:
        """Populate the preview table."""
        table = self.query_one("#recurring-generate-table", DataTable)
        table.cursor_type = "row"
        table.add_column("Date", width=12)
        table.add_column("Description", width=30)
        table.add_column("Amount", width=16)

        for rule, dates in self.pending:
            amount_str = ""
            for posting in rule.postings:
                if posting.amounts:
                    amount_str = posting.amounts[0].format()
                    break

            for d in dates:
                table.add_row(d.isoformat(), rule.description, amount_str)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-recurring-generate":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        """Cancel generation."""
        self.dismiss(False)
