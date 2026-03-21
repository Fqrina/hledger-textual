"""Modal for managing existing CSV rules files."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, Static

from hledger_textual.csv_import import delete_rules_file, get_rules_dir, list_rules_files
from hledger_textual.models import CsvRulesFile


class RulesManagerModal(ModalScreen[tuple[str, CsvRulesFile | None] | None]):
    """Modal for browsing, editing, and deleting CSV rules files.

    Returns:
        ``("select", rules_file)`` — use an existing rules file.
        ``("new", None)`` — create a new rules file via wizard.
        ``("edit", rules_file)`` — edit the selected rules file.
        ``None`` — cancelled.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, journal_file: Path) -> None:
        """Initialize the rules manager.

        Args:
            journal_file: Path to the main journal file.
        """
        super().__init__()
        self.journal_file = journal_file
        self._rules: list[CsvRulesFile] = []

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        with Vertical(id="rules-manager-dialog"):
            yield Label("CSV Import Rules", id="rules-manager-title")
            yield DataTable(id="rules-manager-table")
            yield Static("", id="rules-manager-empty")
            with Horizontal(id="rules-manager-buttons"):
                yield Button("Cancel", variant="default", id="btn-rules-cancel")
                yield Button("Delete", variant="error", id="btn-rules-delete")
                yield Button("Edit", variant="default", id="btn-rules-edit")
                yield Button("+ New", variant="default", id="btn-rules-new")
                yield Button(
                    "Use selected", variant="primary", id="btn-rules-use"
                )

    def on_mount(self) -> None:
        """Load and display rules files."""
        self._refresh_table()

    def _refresh_table(self) -> None:
        """Reload rules from disk and refresh the table."""
        rules_dir = get_rules_dir(self.journal_file)
        self._rules = list_rules_files(rules_dir)

        table = self.query_one("#rules-manager-table", DataTable)
        table.clear(columns=True)

        empty_msg = self.query_one("#rules-manager-empty", Static)

        if not self._rules:
            table.display = False
            empty_msg.update("No rules files found. Create one with '+ New'.")
            empty_msg.display = True
            self.query_one("#btn-rules-delete").display = False
            self.query_one("#btn-rules-edit").display = False
            self.query_one("#btn-rules-use").display = False
            return

        empty_msg.display = False
        table.display = True
        self.query_one("#btn-rules-delete").display = True
        self.query_one("#btn-rules-edit").display = True
        self.query_one("#btn-rules-use").display = True

        table.cursor_type = "row"
        table.add_column("Name", width=24)
        table.add_column("Account", width=28)
        table.add_column("Sep", width=5)

        for rule in self._rules:
            sep_display = repr(rule.separator) if rule.separator == "\t" else rule.separator
            table.add_row(rule.name, rule.account1, sep_display)

    def _get_selected_rule(self) -> CsvRulesFile | None:
        """Return the currently selected rules file, or None."""
        table = self.query_one("#rules-manager-table", DataTable)
        if not self._rules or table.cursor_row is None:
            return None
        idx = table.cursor_row
        if 0 <= idx < len(self._rules):
            return self._rules[idx]
        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        match event.button.id:
            case "btn-rules-cancel":
                self.dismiss(None)
            case "btn-rules-new":
                self.dismiss(("new", None))
            case "btn-rules-use":
                rule = self._get_selected_rule()
                if rule:
                    self.dismiss(("select", rule))
                else:
                    self.notify("No rules file selected", severity="warning", timeout=3)
            case "btn-rules-edit":
                rule = self._get_selected_rule()
                if rule:
                    self.dismiss(("edit", rule))
                else:
                    self.notify("No rules file selected", severity="warning", timeout=3)
            case "btn-rules-delete":
                rule = self._get_selected_rule()
                if rule:
                    delete_rules_file(rule.path)
                    self.notify(f"Deleted {rule.name}", timeout=3)
                    self._refresh_table()

    def action_cancel(self) -> None:
        """Cancel."""
        self.dismiss(None)
