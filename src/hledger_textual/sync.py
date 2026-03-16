"""Sync abstraction layer with pluggable backends.

Provides a unified interface for syncing journal files via different
methods (git, rclone, etc.).  New backends can be added by subclassing
:class:`SyncBackend` and registering them in :func:`create_sync_backend`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class SyncError(Exception):
    """Raised when a sync operation fails."""


class SyncBackend(ABC):
    """Abstract base class for sync backends.

    Each backend provides a name, availability check, and one or more
    sync actions.  The ``actions`` property returns the list of actions
    the user can choose from (e.g. ``["sync"]`` for git, ``["upload",
    "download"]`` for rclone).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable backend name (e.g. ``"Git"``, ``"rclone"``)."""

    @property
    @abstractmethod
    def actions(self) -> list[str]:
        """Available action names for this backend."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether the backend tool is installed and reachable.

        Returns:
            True if the backend can be used.
        """

    @abstractmethod
    def run(self, action: str, journal_file: Path) -> str:
        """Execute a sync action.

        Args:
            action: One of the values from :attr:`actions`.
            journal_file: Path to the hledger journal file.

        Returns:
            A human-readable summary of the result.

        Raises:
            SyncError: If the operation fails.
        """

    @abstractmethod
    def confirm_message(self) -> str:
        """Return a short message for the confirmation dialog.

        Returns:
            A message describing what the sync will do.
        """


class GitSyncBackend(SyncBackend):
    """Sync backend using git (commit + pull --rebase + push)."""

    @property
    def name(self) -> str:
        return "Git"

    @property
    def actions(self) -> list[str]:
        return ["sync"]

    def __init__(self, journal_file: Path) -> None:
        """Initialize with the journal file to check repo status.

        Args:
            journal_file: Path to the hledger journal file.
        """
        self._journal_file = journal_file

    def is_available(self) -> bool:
        """Check that git is installed and the journal is in a repo."""
        from hledger_textual.git import is_git_repo

        return is_git_repo(self._journal_file)

    def run(self, action: str, journal_file: Path) -> str:
        """Execute git sync (commit + pull + push).

        Args:
            action: Must be ``"sync"``.
            journal_file: Path to the hledger journal file.

        Returns:
            Summary of the sync result.

        Raises:
            SyncError: If any git operation fails.
        """
        from hledger_textual.git import GitError, git_sync

        try:
            return git_sync(journal_file)
        except GitError as exc:
            raise SyncError(str(exc)) from exc

    def confirm_message(self) -> str:
        return "Commit, pull, and push via Git?"


class RcloneSyncBackend(SyncBackend):
    """Sync backend using rclone for cloud storage."""

    @property
    def name(self) -> str:
        return "rclone"

    @property
    def actions(self) -> list[str]:
        return ["upload", "download"]

    def __init__(self, config: dict) -> None:
        """Initialize with the rclone configuration.

        Args:
            config: Dict with ``remote`` and ``path`` keys.
        """
        self._config = config

    def is_available(self) -> bool:
        """Check that rclone is installed."""
        from hledger_textual.cloud_sync import has_rclone

        return has_rclone()

    def run(self, action: str, journal_file: Path) -> str:
        """Execute an rclone upload or download.

        Args:
            action: ``"upload"`` or ``"download"``.
            journal_file: Path to the hledger journal file.

        Returns:
            Summary of the sync result.

        Raises:
            SyncError: If the rclone operation fails.
        """
        from hledger_textual.cloud_sync import (
            CloudSyncError,
            cloud_sync_download,
            cloud_sync_upload,
        )

        try:
            if action == "upload":
                return cloud_sync_upload(journal_file, self._config)
            elif action == "download":
                return cloud_sync_download(journal_file, self._config)
            else:
                raise SyncError(f"Unknown action: {action}")
        except CloudSyncError as exc:
            raise SyncError(str(exc)) from exc

    def confirm_message(self) -> str:
        dest = f"{self._config['remote']}:{self._config['path']}"
        return f"Upload or download via rclone ({dest})?"


def create_sync_backend(
    method: str, journal_file: Path, config: dict
) -> SyncBackend:
    """Factory: create the appropriate sync backend.

    Args:
        method: Sync method name (``"git"`` or ``"rclone"``).
        journal_file: Path to the hledger journal file.
        config: The full ``[sync]`` config dict.

    Returns:
        A configured :class:`SyncBackend` instance.

    Raises:
        SyncError: If the method is unknown or misconfigured.
    """
    if method == "git":
        return GitSyncBackend(journal_file)
    elif method == "rclone":
        remote = config.get("remote", "")
        path = config.get("path", "")
        if not remote or not path:
            raise SyncError(
                "rclone sync requires 'remote' and 'path' in [sync] config"
            )
        return RcloneSyncBackend({"remote": remote, "path": path})
    else:
        raise SyncError(f"Unknown sync method: {method!r}")
