"""File backup/restore utilities for safe write operations."""

from __future__ import annotations

import shutil
from pathlib import Path


def backup(file: Path) -> Path:
    """Create a backup of a file.

    Args:
        file: Path to the file to back up.

    Returns:
        Path to the backup file.
    """
    backup_path = file.with_suffix(file.suffix + ".bak")
    shutil.copy2(file, backup_path)
    return backup_path


def restore(file: Path, backup_path: Path) -> None:
    """Restore a file from its backup.

    Args:
        file: Path to the file to restore.
        backup_path: Path to the backup file.
    """
    shutil.copy2(backup_path, file)


def cleanup_backup(backup_path: Path) -> None:
    """Remove a backup file.

    Args:
        backup_path: Path to the backup file to remove.
    """
    backup_path.unlink(missing_ok=True)
