"""Modal screen for browsing and managing saved search filters."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Input, Static

from hledger_textual.config import delete_filter, load_saved_filters, save_filter


class SavedFiltersModal(ModalScreen[str | None]):
    """Browse, apply, save, and delete named search filters.

    When *current_query* is provided a save-as section is shown at the top,
    allowing the user to persist the active filter under a chosen name.

    The modal dismisses with the selected query string when the user presses
    Enter on a row, or with ``None`` when dismissed without a selection.

    Args:
        current_query: The currently active search query.  When non-empty a
            save section is rendered so the user can name and persist it.
    """

    BINDINGS = [
        Binding("escape", "dismiss_none", "Close", show=True),
        Binding("d", "delete_selected", "Delete", show=True),
    ]

    def __init__(self, current_query: str = "", **kwargs) -> None:
        """Initialise the modal.

        Args:
            current_query: Active search query.  Non-empty triggers the save
                section at the top of the dialog.
        """
        super().__init__(**kwargs)
        self._current_query = current_query

    def compose(self) -> ComposeResult:
        """Render the dialog container."""
        with Vertical(id="saved-filters-dialog"):
            yield Static("Saved Filters", id="saved-filters-title")
            if self._current_query:
                yield Static(
                    f"Query: {self._current_query}",
                    id="saved-filters-current-query",
                )
                yield Input(
                    placeholder="Save as… (type a name and press Enter)",
                    id="saved-filters-name-input",
                )
            yield DataTable(id="saved-filters-table", show_cursor=True)
            yield Static(
                "Enter: apply  ·  d: delete  ·  Escape: close",
                id="saved-filters-hint",
            )

    def on_mount(self) -> None:
        """Populate the filters table and focus the appropriate widget."""
        table = self.query_one("#saved-filters-table", DataTable)
        table.cursor_type = "row"
        table.show_header = True
        table.add_column("Name", width=22)
        table.add_column("Query")
        self._reload_table()

        if self._current_query:
            self.query_one("#saved-filters-name-input", Input).focus()
        else:
            table.focus()

    def _reload_table(self) -> None:
        """Clear and repopulate the table from config."""
        table = self.query_one("#saved-filters-table", DataTable)
        table.clear()
        filters = load_saved_filters()
        if not filters:
            table.add_row(
                "[dim]No saved filters yet[/dim]", "", key="__empty__"
            )
        else:
            for name, query in filters.items():
                table.add_row(name, query, key=name)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Save the current filter under the submitted name."""
        name = event.value.strip()
        if not name:
            return
        save_filter(name, self._current_query)
        event.input.value = ""
        self._reload_table()
        self.query_one("#saved-filters-table", DataTable).focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Apply the selected filter and close the modal."""
        key = event.row_key.value if event.row_key else None
        if not key or key == "__empty__":
            return
        filters = load_saved_filters()
        query = filters.get(key)
        if query:
            self.dismiss(query)

    def action_delete_selected(self) -> None:
        """Delete the currently highlighted filter."""
        table = self.query_one("#saved-filters-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        key = row_key.value if row_key else None
        if not key or key == "__empty__":
            return
        delete_filter(key)
        self._reload_table()

    def action_dismiss_none(self) -> None:
        """Close the modal without applying any filter."""
        self.dismiss(None)
