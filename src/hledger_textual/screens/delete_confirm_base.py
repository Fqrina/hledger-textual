"""Reusable base class for delete confirmation modals."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class DeleteConfirmBase(ModalScreen[bool]):
    """Generic delete confirmation modal.

    Subclasses only need to provide CSS id prefixes and summary text
    via constructor arguments.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        title: str,
        summary: str,
        *,
        prefix: str,
    ) -> None:
        """Initialize the modal.

        Args:
            title: The dialog title (e.g. "Delete Transaction?").
            summary: A human-readable summary of the item to delete.
            prefix: CSS id prefix (e.g. "delete", "budget-delete").
        """
        super().__init__()
        self._title = title
        self._summary = summary
        self._prefix = prefix

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        p = self._prefix
        with Vertical(id=f"{p}-dialog"):
            yield Label(self._title, id=f"{p}-title")
            yield Static(self._summary, id=f"{p}-summary")
            with Horizontal(id=f"{p}-buttons"):
                yield Button("Delete", variant="error", id=f"btn-{p}")
                yield Button("Cancel", variant="default", id=f"btn-{p}-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == f"btn-{self._prefix}":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        """Cancel deletion."""
        self.dismiss(False)
