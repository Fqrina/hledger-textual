"""Preview modal for CSV import transactions before writing to journal."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, Static

from hledger_textual.models import Transaction


class ImportPreviewScreen(ModalScreen[list[Transaction] | None]):
    """Preview transactions parsed from CSV before importing.

    Follows the same pattern as :class:`RecurringGenerateScreen`.
    Returns the list of confirmed transactions, or ``None`` on cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        transactions: list[Transaction],
        duplicates_count: int = 0,
    ) -> None:
        """Initialize the preview screen.

        Args:
            transactions: New (non-duplicate) transactions to import.
            duplicates_count: Number of duplicates that were excluded.
        """
        super().__init__()
        self.transactions = transactions
        self.duplicates_count = duplicates_count

    def compose(self) -> ComposeResult:
        """Create the preview layout."""
        count = len(self.transactions)
        summary = f"{count} transaction{'s' if count != 1 else ''} to import"
        if self.duplicates_count > 0:
            summary += (
                f" ({self.duplicates_count} duplicate"
                f"{'s' if self.duplicates_count != 1 else ''} excluded)"
            )

        with Vertical(id="import-preview-dialog"):
            yield Label("Import Preview", id="import-preview-title")
            yield Static(summary, id="import-preview-summary")
            yield DataTable(id="import-preview-table")
            with Horizontal(id="import-preview-buttons"):
                yield Button(
                    "Cancel", variant="default", id="btn-import-cancel"
                )
                yield Button(
                    "Import All", variant="success", id="btn-import-confirm"
                )

    def on_mount(self) -> None:
        """Populate the preview table."""
        table = self.query_one("#import-preview-table", DataTable)
        table.cursor_type = "row"
        table.add_column("Date", width=12)
        table.add_column("Description", width=30)
        table.add_column("Account", width=28)
        table.add_column("Amount", width=16)

        for txn in self.transactions:
            # Find the non-account1 posting for display
            account2 = ""
            amount_str = ""
            for posting in txn.postings:
                if posting.amounts:
                    amount_str = posting.amounts[0].format()
                    account2 = posting.account
                    break
            # If no amount found on first posting, try second
            if not amount_str and len(txn.postings) > 1:
                for posting in txn.postings[1:]:
                    if posting.amounts:
                        amount_str = posting.amounts[0].format()
                        break

            table.add_row(txn.date, txn.description, account2, amount_str)

        if not self.transactions:
            self.query_one("#btn-import-confirm", Button).disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-import-confirm":
            self.dismiss(self.transactions)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel import."""
        self.dismiss(None)
