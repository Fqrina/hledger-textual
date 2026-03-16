"""Unit tests for the sync abstraction layer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from hledger_textual.sync import (
    GitSyncBackend,
    RcloneSyncBackend,
    SyncError,
    create_sync_backend,
)


# -- GitSyncBackend ---------------------------------------------------------


def test_git_backend_name():
    """GitSyncBackend reports its name as 'Git'."""
    backend = GitSyncBackend(Path("/tmp/test.journal"))
    assert backend.name == "Git"


def test_git_backend_actions():
    """GitSyncBackend has a single 'sync' action."""
    backend = GitSyncBackend(Path("/tmp/test.journal"))
    assert backend.actions == ["sync"]


def test_git_backend_confirm_message():
    """GitSyncBackend provides a confirmation message."""
    backend = GitSyncBackend(Path("/tmp/test.journal"))
    assert "Git" in backend.confirm_message()


def test_git_backend_is_available_true():
    """GitSyncBackend is available when journal is in a git repo."""
    backend = GitSyncBackend(Path("/tmp/test.journal"))
    with patch("hledger_textual.git.is_git_repo", return_value=True):
        assert backend.is_available() is True


def test_git_backend_is_available_false():
    """GitSyncBackend is unavailable when journal is not in a git repo."""
    backend = GitSyncBackend(Path("/tmp/test.journal"))
    with patch("hledger_textual.git.is_git_repo", return_value=False):
        assert backend.is_available() is False


def test_git_backend_run_success():
    """GitSyncBackend.run delegates to git_sync and returns result."""
    backend = GitSyncBackend(Path("/tmp/test.journal"))
    with patch(
        "hledger_textual.git.git_sync",
        return_value="Committed and pushed successfully",
    ):
        result = backend.run("sync", Path("/tmp/test.journal"))
        assert result == "Committed and pushed successfully"


def test_git_backend_run_error():
    """GitSyncBackend.run wraps GitError as SyncError."""
    from hledger_textual.git import GitError

    backend = GitSyncBackend(Path("/tmp/test.journal"))
    with patch("hledger_textual.git.git_sync", side_effect=GitError("conflict")):
        with pytest.raises(SyncError, match="conflict"):
            backend.run("sync", Path("/tmp/test.journal"))


# -- RcloneSyncBackend ------------------------------------------------------


def test_rclone_backend_name():
    """RcloneSyncBackend reports its name as 'rclone'."""
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    assert backend.name == "rclone"


def test_rclone_backend_actions():
    """RcloneSyncBackend has upload and download actions."""
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    assert backend.actions == ["upload", "download"]


def test_rclone_backend_confirm_message():
    """RcloneSyncBackend shows the remote destination in its message."""
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    msg = backend.confirm_message()
    assert "gdrive:backup" in msg


def test_rclone_backend_is_available_true():
    """RcloneSyncBackend is available when rclone is installed."""
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    with patch("hledger_textual.cloud_sync.has_rclone", return_value=True):
        assert backend.is_available() is True


def test_rclone_backend_is_available_false():
    """RcloneSyncBackend is unavailable when rclone is not installed."""
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    with patch("hledger_textual.cloud_sync.has_rclone", return_value=False):
        assert backend.is_available() is False


def test_rclone_backend_run_upload(tmp_path):
    """RcloneSyncBackend.run('upload') delegates to cloud_sync_upload."""
    journal = tmp_path / "test.journal"
    journal.write_text("2026-01-01 test\n")
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    with patch(
        "hledger_textual.cloud_sync.cloud_sync_upload",
        return_value="Uploaded to gdrive:backup",
    ):
        result = backend.run("upload", journal)
        assert "Uploaded" in result


def test_rclone_backend_run_download(tmp_path):
    """RcloneSyncBackend.run('download') delegates to cloud_sync_download."""
    journal = tmp_path / "test.journal"
    journal.write_text("2026-01-01 test\n")
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    with patch(
        "hledger_textual.cloud_sync.cloud_sync_download",
        return_value="Downloaded from gdrive:backup",
    ):
        result = backend.run("download", journal)
        assert "Downloaded" in result


def test_rclone_backend_run_error(tmp_path):
    """RcloneSyncBackend.run wraps CloudSyncError as SyncError."""
    from hledger_textual.cloud_sync import CloudSyncError

    journal = tmp_path / "test.journal"
    journal.write_text("2026-01-01 test\n")
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    with patch(
        "hledger_textual.cloud_sync.cloud_sync_upload",
        side_effect=CloudSyncError("permission denied"),
    ):
        with pytest.raises(SyncError, match="permission denied"):
            backend.run("upload", journal)


def test_rclone_backend_run_unknown_action():
    """RcloneSyncBackend.run raises SyncError for unknown actions."""
    backend = RcloneSyncBackend({"remote": "gdrive", "path": "backup"})
    with pytest.raises(SyncError, match="Unknown action"):
        backend.run("invalid", Path("/tmp/test.journal"))


# -- create_sync_backend factory --------------------------------------------


def test_create_sync_backend_git():
    """create_sync_backend('git') returns a GitSyncBackend."""
    backend = create_sync_backend("git", Path("/tmp/test.journal"), {})
    assert isinstance(backend, GitSyncBackend)


def test_create_sync_backend_rclone():
    """create_sync_backend('rclone') returns a RcloneSyncBackend."""
    config = {"remote": "gdrive", "path": "backup"}
    backend = create_sync_backend("rclone", Path("/tmp/test.journal"), config)
    assert isinstance(backend, RcloneSyncBackend)


def test_create_sync_backend_rclone_missing_remote():
    """create_sync_backend('rclone') raises SyncError without remote."""
    with pytest.raises(SyncError, match="remote"):
        create_sync_backend("rclone", Path("/tmp/test.journal"), {"path": "backup"})


def test_create_sync_backend_rclone_missing_path():
    """create_sync_backend('rclone') raises SyncError without path."""
    with pytest.raises(SyncError, match="remote"):
        create_sync_backend("rclone", Path("/tmp/test.journal"), {"remote": "gdrive"})


def test_create_sync_backend_unknown_method():
    """create_sync_backend raises SyncError for unknown methods."""
    with pytest.raises(SyncError, match="Unknown sync method"):
        create_sync_backend("dropbox", Path("/tmp/test.journal"), {})
