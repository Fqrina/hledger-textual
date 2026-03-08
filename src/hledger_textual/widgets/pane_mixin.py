"""Shared mixin for pane widgets backed by a DataTable."""

from __future__ import annotations

from textual.widgets import DataTable

from hledger_textual.widgets import distribute_column_widths


class DataTablePaneMixin:
    """Mixin providing on_show, on_resize, and cursor navigation for DataTable panes.

    Subclasses must set ``_main_table_id`` (the CSS id of their DataTable)
    and ``_fixed_column_widths`` (a dict of column-index to fixed width).
    """

    _main_table_id: str
    _fixed_column_widths: dict[int, int] = {}

    def _get_main_table(self) -> DataTable:
        """Return the pane's primary DataTable."""
        return self.query_one(f"#{self._main_table_id}", DataTable)

    def on_show(self) -> None:
        """Restore focus to the table when the pane becomes visible."""
        self._get_main_table().focus()

    def on_resize(self) -> None:
        """Recalculate column widths when the pane is resized."""
        distribute_column_widths(self._get_main_table(), self._fixed_column_widths)

    def action_cursor_down(self) -> None:
        """Move cursor down in the table."""
        self._get_main_table().action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in the table."""
        self._get_main_table().action_cursor_up()
