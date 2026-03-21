"""Delete confirmation modal for custom reports."""

from __future__ import annotations

from hledger_textual.screens.delete_confirm_base import DeleteConfirmBase


class CustomReportDeleteConfirmModal(DeleteConfirmBase):
    """A modal dialog to confirm custom report deletion."""

    def __init__(self, name: str) -> None:
        """Initialize the modal.

        Args:
            name: The custom report name to confirm deletion of.
        """
        super().__init__(
            title="Delete Custom Report?",
            summary=name,
            prefix="custom-report-delete",
        )
