"""Delete confirmation modal for budget rules."""

from __future__ import annotations

from hledger_textual.models import BudgetRule
from hledger_textual.screens.delete_confirm_base import DeleteConfirmBase


class BudgetDeleteConfirmModal(DeleteConfirmBase):
    """A modal dialog to confirm budget rule deletion."""

    def __init__(self, rule: BudgetRule) -> None:
        """Initialize the modal.

        Args:
            rule: The budget rule to confirm deletion of.
        """
        super().__init__(
            title="Delete Budget Rule?",
            summary=f"{rule.account}  {rule.amount.format()}",
            prefix="budget-delete",
        )
