"""Update check module: queries PyPI for the latest version with a 24-hour cache."""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

_CACHE_PATH = Path.home() / ".cache" / "hledger-textual" / "update_check.json"
_PYPI_URL = "https://pypi.org/pypi/hledger-textual/json"
_CACHE_TTL = timedelta(hours=24)


def _fetch_latest_version() -> str | None:
    """Fetch the latest published version from PyPI.

    Returns:
        Version string (e.g. ``"0.1.8"``), or ``None`` on any error.
    """
    try:
        with urllib.request.urlopen(_PYPI_URL, timeout=5) as resp:  # noqa: S310
            data = json.loads(resp.read())
            return data["info"]["version"]
    except Exception:
        return None


def _read_cache() -> tuple[str | None, datetime | None]:
    """Read the cached latest version and its timestamp.

    Returns:
        ``(version, checked_at)`` tuple; both ``None`` if the cache is absent
        or unreadable.
    """
    try:
        with open(_CACHE_PATH) as f:
            data = json.load(f)
        return data["latest_version"], datetime.fromisoformat(data["checked_at"])
    except Exception:
        return None, None


def _write_cache(version: str) -> None:
    """Persist the latest version and current timestamp to the cache file."""
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_CACHE_PATH, "w") as f:
            json.dump(
                {"latest_version": version, "checked_at": datetime.now().isoformat()},
                f,
            )
    except Exception:
        pass


def get_latest_version() -> str | None:
    """Return the latest hledger-textual version from PyPI, with a 24-hour cache.

    Reads the local cache first. Fetches from PyPI only when the cache is
    absent or older than 24 hours. Falls back to the stale cached value if
    the network request fails.

    Returns:
        Version string (e.g. ``"0.1.8"``), or ``None`` if unavailable.
    """
    cached_version, checked_at = _read_cache()
    cache_fresh = (
        cached_version is not None
        and checked_at is not None
        and datetime.now() - checked_at < _CACHE_TTL
    )
    if cache_fresh:
        return cached_version

    fetched = _fetch_latest_version()
    if fetched:
        _write_cache(fetched)
        return fetched

    # Network failed — return stale cache rather than nothing
    return cached_version


def is_newer(latest: str, current: str) -> bool:
    """Return True if *latest* is strictly newer than *current*.

    Compares using tuple comparison of integer version components so that
    ``"0.1.10"`` is correctly treated as newer than ``"0.1.9"``.

    Args:
        latest: The version string fetched from PyPI.
        current: The installed version string.

    Returns:
        ``True`` if an upgrade is available.
    """
    def _parse(v: str) -> tuple[int, ...]:
        try:
            return tuple(int(x) for x in v.split("."))
        except ValueError:
            return (0,)

    return _parse(latest) > _parse(current)
