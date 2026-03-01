"""Tests for file backup/restore utilities."""

from pathlib import Path

from hledger_textual.fileutil import backup, cleanup_backup, restore


class TestBackup:
    """Tests for backup."""

    def test_creates_bak_file(self, tmp_path: Path):
        """A .bak file is created next to the original."""
        f = tmp_path / "test.journal"
        f.write_text("original content")
        bak = backup(f)
        assert bak == tmp_path / "test.journal.bak"
        assert bak.exists()

    def test_backup_content_matches_original(self, tmp_path: Path):
        """The backup has the same content as the original."""
        f = tmp_path / "test.journal"
        f.write_text("some data")
        bak = backup(f)
        assert bak.read_text() == "some data"

    def test_original_is_unchanged(self, tmp_path: Path):
        """The original file is not modified."""
        f = tmp_path / "test.journal"
        f.write_text("keep me")
        backup(f)
        assert f.read_text() == "keep me"

    def test_compound_extension(self, tmp_path: Path):
        """Files with compound extensions get .bak appended to the last suffix."""
        f = tmp_path / "data.budget.journal"
        f.write_text("budget data")
        bak = backup(f)
        assert bak.name == "data.budget.journal.bak"
        assert bak.read_text() == "budget data"


class TestRestore:
    """Tests for restore."""

    def test_overwrites_original_with_backup(self, tmp_path: Path):
        """Restore replaces the original file content with the backup."""
        f = tmp_path / "test.journal"
        f.write_text("original")
        bak = backup(f)
        f.write_text("modified")
        restore(f, bak)
        assert f.read_text() == "original"

    def test_backup_still_exists_after_restore(self, tmp_path: Path):
        """The backup file is not removed by restore."""
        f = tmp_path / "test.journal"
        f.write_text("data")
        bak = backup(f)
        f.write_text("changed")
        restore(f, bak)
        assert bak.exists()


class TestCleanupBackup:
    """Tests for cleanup_backup."""

    def test_removes_backup_file(self, tmp_path: Path):
        """The backup file is deleted."""
        bak = tmp_path / "test.journal.bak"
        bak.write_text("backup")
        cleanup_backup(bak)
        assert not bak.exists()

    def test_no_error_when_missing(self, tmp_path: Path):
        """No exception is raised when the backup file does not exist."""
        bak = tmp_path / "nonexistent.bak"
        cleanup_backup(bak)  # should not raise


class TestRoundtrip:
    """End-to-end backup/mutate/restore/cleanup cycle."""

    def test_full_cycle(self, tmp_path: Path):
        """Backup, modify, restore, cleanup returns to original state."""
        f = tmp_path / "test.journal"
        f.write_text("original content")

        bak = backup(f)
        f.write_text("corrupted content")
        restore(f, bak)
        assert f.read_text() == "original content"

        cleanup_backup(bak)
        assert not bak.exists()
        assert f.exists()
