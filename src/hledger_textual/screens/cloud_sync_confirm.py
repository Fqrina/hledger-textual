"""Cloud sync confirmation modal screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class CloudSyncConfirmModal(ModalScreen[str | None]):
    """A modal dialog to choose a cloud sync action.

    Returns ``"upload"``, ``"download"``, or ``None`` (cancel).
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        with Vertical(id="cloud-sync-dialog"):
            yield Label("Cloud Sync", id="cloud-sync-title")
            yield Label(
                "Upload your journal to the cloud or download from it?",
                id="cloud-sync-summary",
            )
            with Horizontal(id="cloud-sync-buttons"):
                yield Button("Cancel", variant="default", id="btn-cloud-cancel")
                yield Button("Download", variant="warning", id="btn-cloud-download")
                yield Button("Upload", variant="primary", id="btn-cloud-upload")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-cloud-upload":
            self.dismiss("upload")
        elif event.button.id == "btn-cloud-download":
            self.dismiss("download")
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel cloud sync."""
        self.dismiss(None)
