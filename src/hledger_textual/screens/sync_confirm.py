"""Sync confirmation modal screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from hledger_textual.sync import SyncBackend


class SyncConfirmModal(ModalScreen[str | None]):
    """A modal dialog to confirm and choose a sync action.

    Adapts its buttons to the backend's available actions.
    Returns the chosen action string, or ``None`` on cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, backend: SyncBackend) -> None:
        """Initialize the modal.

        Args:
            backend: The sync backend to display actions for.
        """
        super().__init__()
        self._backend = backend

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        with Vertical(id="sync-dialog"):
            yield Label(f"Sync ({self._backend.name})", id="sync-title")
            yield Label(self._backend.confirm_message(), id="sync-summary")
            with Horizontal(id="sync-buttons"):
                yield Button("Cancel", variant="default", id="btn-sync-cancel")
                actions = self._backend.actions
                if len(actions) == 1:
                    yield Button(
                        actions[0].capitalize(),
                        variant="primary",
                        id=f"btn-sync-{actions[0]}",
                    )
                else:
                    for action in actions:
                        variant = "primary" if action == actions[-1] else "warning"
                        yield Button(
                            action.capitalize(),
                            variant=variant,
                            id=f"btn-sync-{action}",
                        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        btn_id = event.button.id or ""
        if btn_id.startswith("btn-sync-") and btn_id != "btn-sync-cancel":
            action = btn_id.removeprefix("btn-sync-")
            self.dismiss(action)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel sync."""
        self.dismiss(None)
