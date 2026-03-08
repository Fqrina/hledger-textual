"""Delete confirmation modal screen for transactions."""

from __future__ import annotations

from hledger_textual.models import Transaction
from hledger_textual.screens.delete_confirm_base import DeleteConfirmBase


class DeleteConfirmModal(DeleteConfirmBase):
    """A modal dialog to confirm transaction deletion."""

    def __init__(self, transaction: Transaction) -> None:
        """Initialize the modal.

        Args:
            transaction: The transaction to confirm deletion of.
        """
        status = f" {transaction.status.symbol}" if transaction.status.symbol else ""
        summary = f"{transaction.date}{status} {transaction.description}"
        postings_summary = "\n".join(
            f"  {p.account}" for p in transaction.postings
        )
        super().__init__(
            title="Delete Transaction?",
            summary=f"{summary}\n{postings_summary}",
            prefix="delete",
        )
