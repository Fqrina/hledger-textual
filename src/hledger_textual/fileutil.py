"""File backup/restore utilities for safe write operations."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable


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


def safe_write_with_validation(
    target_file: Path,
    content: str,
    journal_file: Path,
    validate: Callable[[Path], None],
    error_cls: type[Exception],
    context: str = "file",
) -> None:
    """Write content to a file with backup/validate/restore safety.

    1. Creates a backup of *target_file*.
    2. Writes *content* to *target_file*.
    3. Calls *validate(journal_file)* to check validity.
    4. On validation failure, restores from backup and raises *error_cls*.

    Args:
        target_file: The file to write to.
        content: The new file content.
        journal_file: Path to the main journal file (passed to validate).
        validate: A callable that raises on validation failure.
        error_cls: The exception class to raise on failure.
        context: A label for error messages (e.g. "Budget", "Recurring").
    """
    bak = backup(target_file)

    try:
        target_file.write_text(content)

        try:
            validate(journal_file)
        except Exception as exc:
            restore(target_file, bak)
            cleanup_backup(bak)
            raise error_cls(
                f"{context} validation failed, changes reverted: {exc}"
            ) from exc

        cleanup_backup(bak)
    except error_cls:
        raise
    except Exception as exc:
        restore(target_file, bak)
        cleanup_backup(bak)
        raise error_cls(f"Failed to write {context.lower()}: {exc}") from exc
