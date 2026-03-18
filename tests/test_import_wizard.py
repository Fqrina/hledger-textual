"""UI tests for the CSV import wizard and preview screens."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from hledger_textual.csv_import import generate_rules_content, save_rules_file

_has_hledger = shutil.which("hledger") is not None

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_CSV = FIXTURES / "sample_bank.csv"
SAMPLE_RULES = FIXTURES / "sample_bank.rules"


class TestCsvFileSelectModal:
    """Tests for the CsvFileSelectModal screen."""

    @pytest.mark.asyncio
    async def test_dismiss_with_valid_path(self) -> None:
        """Dismissing with a valid CSV path should return the path."""
        from hledger_textual.screens.csv_file_select import CsvFileSelectModal

        results: list = []

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(
                    CsvFileSelectModal(), callback=lambda r: results.append(r)
                )

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            inp = app.screen.query_one("#csv-file-path-input")
            inp.value = str(SAMPLE_CSV)
            btn = app.screen.query_one("#btn-csv-next")
            await pilot.click(btn)
            await pilot.pause()

        assert len(results) == 1
        assert results[0] == SAMPLE_CSV.resolve()

    @pytest.mark.asyncio
    async def test_dismiss_with_cancel(self) -> None:
        """Cancelling should return None."""
        from hledger_textual.screens.csv_file_select import CsvFileSelectModal

        results: list = []

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(
                    CsvFileSelectModal(), callback=lambda r: results.append(r)
                )

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#btn-csv-cancel")
            await pilot.click(btn)
            await pilot.pause()

        assert results == [None]

    @pytest.mark.asyncio
    async def test_invalid_path_keeps_modal_open(self) -> None:
        """An invalid path should not dismiss the modal."""
        from hledger_textual.screens.csv_file_select import CsvFileSelectModal

        results: list = []

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(
                    CsvFileSelectModal(), callback=lambda r: results.append(r)
                )

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            inp = app.screen.query_one("#csv-file-path-input")
            inp.value = "/nonexistent/path/file.csv"
            btn = app.screen.query_one("#btn-csv-next")
            await pilot.click(btn)
            await pilot.pause()
            # Modal should still be open (no result yet)
            assert len(results) == 0


class TestRulesManagerModal:
    """Tests for the RulesManagerModal screen."""

    @pytest.mark.asyncio
    async def test_empty_rules_dir(self, tmp_path: Path) -> None:
        """With no rules files, should show empty message."""
        from hledger_textual.screens.rules_manager import RulesManagerModal

        journal = tmp_path / "test.journal"
        journal.write_text("")

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(RulesManagerModal(journal))

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            empty_msg = app.screen.query_one("#rules-manager-empty")
            assert empty_msg.display is True

    @pytest.mark.asyncio
    async def test_new_button_returns_new(self, tmp_path: Path) -> None:
        """Clicking '+ New' should dismiss with ('new', None)."""
        from hledger_textual.screens.rules_manager import RulesManagerModal

        journal = tmp_path / "test.journal"
        journal.write_text("")
        results: list = []

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(
                    RulesManagerModal(journal), callback=lambda r: results.append(r)
                )

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#btn-rules-new")
            await pilot.click(btn)
            await pilot.pause()

        assert results == [("new", None)]

    @pytest.mark.asyncio
    async def test_lists_existing_rules(self, tmp_path: Path) -> None:
        """Should display rules files found in the rules directory."""
        from textual.widgets import DataTable

        from hledger_textual.screens.rules_manager import RulesManagerModal

        journal = tmp_path / "test.journal"
        journal.write_text("")
        rules_dir = tmp_path / "rules"
        rules_dir.mkdir()
        content = generate_rules_content(
            name="Test Bank", separator=",", date_format="%Y-%m-%d",
            skip=1, field_mapping=["date", "description", "amount"],
            currency="EUR", account1="assets:bank:test", conditional_rules=[],
        )
        save_rules_file(rules_dir, "Test Bank", content)

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(RulesManagerModal(journal))

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.screen.query_one("#rules-manager-table", DataTable)
            assert table.row_count == 1


@pytest.mark.skipif(not _has_hledger, reason="hledger not installed")
class TestImportPreviewScreen:
    """Tests for the ImportPreviewScreen."""

    @pytest.mark.asyncio
    async def test_shows_transactions(self) -> None:
        """Should display the transactions in a DataTable."""
        from textual.widgets import DataTable

        from hledger_textual.csv_import import preview_import
        from hledger_textual.screens.import_preview import ImportPreviewScreen

        txns = preview_import(SAMPLE_CSV, SAMPLE_RULES)

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(ImportPreviewScreen(txns, duplicates_count=0))

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.screen.query_one("#import-preview-table", DataTable)
            assert table.row_count == 26

    @pytest.mark.asyncio
    async def test_cancel_returns_none(self) -> None:
        """Cancelling should return None."""
        from textual.widgets import Button

        from hledger_textual.csv_import import preview_import
        from hledger_textual.screens.import_preview import ImportPreviewScreen

        txns = preview_import(SAMPLE_CSV, SAMPLE_RULES)
        results: list = []

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(
                    ImportPreviewScreen(txns), callback=lambda r: results.append(r)
                )

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#btn-import-cancel", Button)
            btn.press()
            await pilot.pause()

        assert results == [None]

    @pytest.mark.asyncio
    async def test_import_returns_transactions(self) -> None:
        """Confirming should return the transaction list."""
        from textual.widgets import Button

        from hledger_textual.csv_import import preview_import
        from hledger_textual.screens.import_preview import ImportPreviewScreen

        txns = preview_import(SAMPLE_CSV, SAMPLE_RULES)
        results: list = []

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(
                    ImportPreviewScreen(txns), callback=lambda r: results.append(r)
                )

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#btn-import-confirm", Button)
            btn.press()
            await pilot.pause()

        assert len(results) == 1
        assert len(results[0]) == 26

    @pytest.mark.asyncio
    async def test_duplicates_count_shown(self) -> None:
        """The summary should mention excluded duplicates."""
        from hledger_textual.csv_import import preview_import
        from hledger_textual.screens.import_preview import ImportPreviewScreen

        txns = preview_import(SAMPLE_CSV, SAMPLE_RULES)

        class _App(App):
            def compose(self) -> ComposeResult:
                yield Static("test")

            def on_mount(self) -> None:
                self.push_screen(ImportPreviewScreen(txns[:3], duplicates_count=2))

        app = _App()
        async with app.run_test() as pilot:
            await pilot.pause()
            summary = app.screen.query_one("#import-preview-summary")
            rendered = str(summary.renderable)
            assert "2 duplicates excluded" in rendered
