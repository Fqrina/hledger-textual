"""Delete confirmation modal for recurring rules."""

from __future__ import annotations

from hledger_textual.models import RecurringRule
from hledger_textual.screens.delete_confirm_base import DeleteConfirmBase


class RecurringDeleteConfirmModal(DeleteConfirmBase):
    """A modal dialog to confirm recurring rule deletion."""

    def __init__(self, rule: RecurringRule) -> None:
        """Initialize the modal.

        Args:
            rule: The recurring rule to confirm deletion of.
        """
        super().__init__(
            title="Delete Recurring Rule?",
            summary=f"{rule.period_expr}  {rule.description}",
            prefix="recurring-delete",
        )
