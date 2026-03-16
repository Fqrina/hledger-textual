"""Export format selection modal screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet


class ExportModal(ModalScreen[tuple[str, str, str] | None]):
    """Modal for choosing export format (CSV/PDF), filename, and directory.

    Returns a ``(format, filename, directory)`` tuple on confirm, or ``None``
    on cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        default_filename: str = "export.csv",
        default_directory: str = "",
    ) -> None:
        """Initialize the modal.

        Args:
            default_filename: Pre-filled filename suggestion.
            default_directory: Pre-filled export directory path.
        """
        super().__init__()
        self._default_filename = default_filename
        self._default_directory = default_directory

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        with Vertical(id="export-dialog"):
            yield Label("Export Data", id="export-title")
            yield Label("Format:", id="export-format-label")
            with RadioSet(id="export-format"):
                yield RadioButton("CSV", value=True, id="radio-csv")
                yield RadioButton("PDF", id="radio-pdf")
            yield Label("Directory:", id="export-dir-label")
            yield Input(
                value=self._default_directory,
                id="export-dir-input",
            )
            yield Label("Filename:", id="export-filename-label")
            yield Input(
                value=self._default_filename,
                id="export-filename-input",
            )
            with Horizontal(id="export-buttons"):
                yield Button("Cancel", variant="default", id="btn-export-cancel")
                yield Button("Export", variant="primary", id="btn-export")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Update filename extension when format changes."""
        inp = self.query_one("#export-filename-input", Input)
        current = inp.value
        if event.pressed.id == "radio-pdf":
            if current.endswith(".csv"):
                inp.value = current[:-4] + ".pdf"
        elif event.pressed.id == "radio-csv":
            if current.endswith(".pdf"):
                inp.value = current[:-4] + ".csv"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-export":
            fmt = "pdf" if self.query_one("#radio-pdf", RadioButton).value else "csv"
            filename = self.query_one("#export-filename-input", Input).value.strip()
            directory = self.query_one("#export-dir-input", Input).value.strip()
            if not filename:
                self.notify("Please enter a filename", severity="warning", timeout=3)
            elif not directory:
                self.notify("Please enter a directory", severity="warning", timeout=3)
            else:
                self.dismiss((fmt, filename, directory))
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel export."""
        self.dismiss(None)
