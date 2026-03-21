"""Modal for selecting a CSV file to import."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class CsvFileSelectModal(ModalScreen[Path | None]):
    """Simple modal to select a CSV file path.

    Validates that the path exists, is a file, and is readable.
    Returns the resolved :class:`Path` on success, or ``None`` on cancel.
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        """Create the modal layout."""
        default_dir = str(Path.home() / "Downloads") + "/"
        with Vertical(id="csv-file-select-dialog"):
            yield Label("Select CSV File", id="csv-file-select-title")
            yield Label("File path:", id="csv-file-select-label")
            yield Input(
                value=default_dir,
                placeholder="~/Downloads/bank_export.csv",
                id="csv-file-path-input",
            )
            with Horizontal(id="csv-file-select-buttons"):
                yield Button("Cancel", variant="default", id="btn-csv-cancel")
                yield Button("Next", variant="primary", id="btn-csv-next")

    def on_mount(self) -> None:
        """Focus the file path input on mount."""
        self.query_one("#csv-file-path-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-csv-next":
            self._validate_and_proceed()
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in the input."""
        if event.input.id == "csv-file-path-input":
            self._validate_and_proceed()

    def _validate_and_proceed(self) -> None:
        """Validate the file path and dismiss with the path if valid."""
        raw = self.query_one("#csv-file-path-input", Input).value.strip()
        if not raw:
            self.notify("Please enter a file path", severity="warning", timeout=3)
            return

        path = Path(raw).expanduser().resolve()
        if not path.exists():
            self.notify(f"File not found: {path}", severity="error", timeout=5)
            return
        if not path.is_file():
            self.notify(f"Not a file: {path}", severity="error", timeout=5)
            return
        if path.suffix.lower() not in (".csv", ".tsv", ".txt"):
            self.notify(
                "Expected a .csv, .tsv, or .txt file",
                severity="warning",
                timeout=5,
            )
            # Still allow proceeding — just a warning

        self.dismiss(path)

    def action_cancel(self) -> None:
        """Cancel file selection."""
        self.dismiss(None)
