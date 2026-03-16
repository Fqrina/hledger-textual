"""Thread-safe cache for hledger subprocess results."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any


class HledgerCache:
    """Thread-safe cache keyed by (args_tuple, file_mtime).

    Stores the results of hledger CLI calls and returns cached values
    when the same arguments are used and the journal file has not been
    modified since the last call.
    """

    def __init__(self) -> None:
        """Initialize an empty cache."""
        self._lock = threading.Lock()
        self._store: dict[tuple, Any] = {}

    def _file_mtime(self, file: str | Path | None) -> float:
        """Return the mtime of *file*, or 0.0 if unavailable.

        Args:
            file: Path to the journal file.

        Returns:
            Modification time as a float, or 0.0.
        """
        if file is None:
            return 0.0
        try:
            return Path(file).stat().st_mtime
        except OSError:
            return 0.0

    def get(self, args: tuple, file: str | Path | None = None) -> Any | None:
        """Return a cached result, or ``None`` on miss.

        Args:
            args: The hledger argument tuple used as cache key.
            file: Path to the journal file (mtime is checked).

        Returns:
            The cached result, or ``None`` if not found or stale.
        """
        mtime = self._file_mtime(file)
        key = (args, mtime)
        with self._lock:
            return self._store.get(key)

    def put(self, args: tuple, result: Any, file: str | Path | None = None) -> None:
        """Store a result in the cache.

        Args:
            args: The hledger argument tuple used as cache key.
            result: The value to cache.
            file: Path to the journal file (mtime is recorded).
        """
        mtime = self._file_mtime(file)
        key = (args, mtime)
        with self._lock:
            self._store[key] = result

    def invalidate_all(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        """Return the number of cached entries."""
        with self._lock:
            return len(self._store)
