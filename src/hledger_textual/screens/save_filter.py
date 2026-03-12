"""Modal screen for saving the current search filter with a name."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

from hledger_textual.config import save_filter


class SaveFilterModal(ModalScreen[None]):
    """Prompt the user for a name and persist the active search filter.

    Args:
        current_query: The hledger query string to save.
    """

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Cancel", show=True),
    ]

    def __init__(self, current_query: str, **kwargs) -> None:
        """Initialise the modal.

        Args:
            current_query: The active search query to persist.
        """
        super().__init__(**kwargs)
        self._current_query = current_query

    def compose(self) -> ComposeResult:
        """Render the save dialog."""
        with Vertical(id="save-filter-dialog"):
            yield Static("Save Filter", id="save-filter-title")
            yield Static(
                f"Query: {self._current_query}",
                id="save-filter-query",
            )
            yield Input(
                placeholder="Filter name… (press Enter to save)",
                id="save-filter-name-input",
            )
            yield Static(
                "Enter: save  ·  Escape: cancel",
                id="save-filter-hint",
            )

    def on_mount(self) -> None:
        """Focus the name input."""
        self.query_one("#save-filter-name-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Save the filter and close the modal."""
        name = event.value.strip()
        if not name:
            return
        save_filter(name, self._current_query)
        self.dismiss(None)

    def action_dismiss_modal(self) -> None:
        """Close without saving."""
        self.dismiss(None)
