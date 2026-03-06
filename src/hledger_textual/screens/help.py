"""Help screen showing all keyboard shortcuts."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

def _row(key: str, desc: str) -> str:
    """Format a single shortcut row with fixed-width key column."""
    return f"  {key:<14}{desc}"


def _build_help_text() -> str:
    """Build the full help text with aligned columns."""
    sections = [
        (
            "Global",
            [
                ("1-7", "Switch tab"),
                ("s", "Git Sync"),
                ("?", "This help"),
                ("q", "Quit"),
            ],
        ),
        (
            "Transactions",
            [
                ("a", "Add transaction"),
                ("e / Enter", "Edit transaction"),
                ("d", "Delete transaction"),
                ("c", "Clone transaction"),
                ("m", "Move to another date"),
                ("*", "Toggle cleared"),
                ("!", "Toggle pending"),
                ("Left / Right", "Navigate months"),
                ("t", "Jump to today"),
                ("/", "Search"),
                ("r", "Refresh"),
            ],
        ),
        (
            "Recurring",
            [
                ("a", "Add rule"),
                ("e / Enter", "Edit rule"),
                ("d", "Delete rule"),
                ("g", "Generate transactions"),
                ("r", "Reload"),
            ],
        ),
        (
            "Budget",
            [
                ("a", "Add rule"),
                ("e", "Edit rule"),
                ("d", "Delete rule"),
                ("Left / Right", "Navigate months"),
                ("t", "Jump to today"),
                ("/", "Search"),
            ],
        ),
        (
            "Accounts",
            [
                ("Enter", "Drill down"),
                ("/", "Search"),
                ("r", "Reload"),
            ],
        ),
        (
            "Reports",
            [
                ("c", "Toggle chart"),
                ("i", "Investment view"),
                ("r", "Reload"),
            ],
        ),
        (
            "Info",
            [
                ("t", "Theme picker"),
            ],
        ),
    ]
    parts: list[str] = []
    for title, shortcuts in sections:
        parts.append(f"[b]{title}[/b]")
        for key, desc in shortcuts:
            parts.append(_row(key, desc))
        parts.append("")
    return "\n".join(parts).rstrip()


_HELP_TEXT = _build_help_text()


class HelpScreen(ModalScreen[None]):
    """Modal showing all keyboard shortcuts."""

    BINDINGS = [
        Binding("escape", "dismiss_help", "Close"),
        Binding("question_mark", "dismiss_help", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Create the help dialog layout."""
        with VerticalScroll(id="help-dialog"):
            yield Static("Keyboard Shortcuts", id="help-title")
            yield Static(_HELP_TEXT, id="help-content")
            yield Static(
                "Press [b]Esc[/b] or [b]?[/b] to close", id="help-footer"
            )

    def action_dismiss_help(self) -> None:
        """Close the help screen."""
        self.dismiss(None)
