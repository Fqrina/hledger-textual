"""Main Textual application for hledger-textual."""

from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import ContentSwitcher, DataTable, Static, Tab, Tabs

from hledger_textual.config import load_auto_generate_recurring, load_theme
from hledger_textual.widgets.accounts_pane import AccountsPane
from hledger_textual.widgets.budget_pane import BudgetPane
from hledger_textual.widgets.recurring_pane import RecurringPane
from hledger_textual.widgets.reports_pane import ReportsPane
from hledger_textual.widgets.summary_pane import SummaryPane
from hledger_textual.widgets.transactions_pane import TransactionsPane
from hledger_textual.widgets.transactions_table import TransactionsTable

_FOOTER_GLOBAL = "\\[s] Sync  \\[?] Help  \\[q] Quit"

_FOOTER_COMMANDS: dict[str, str] = {
    "summary": f"\\[r] Reload  {_FOOTER_GLOBAL}",
    "transactions": f"\\[a] Add  \\[e] Edit  \\[d] Del  \\[c] Clone  \\[m] Move  \\[◄/►] Month  \\[/] Search  \\[f] Filters  \\[^s] Save filter  {_FOOTER_GLOBAL}",
    "accounts": f"\\[↵] Drill  \\[/] Search  \\[r] Reload  {_FOOTER_GLOBAL}",
    "budget": f"\\[a] Add  \\[e] Edit  \\[d] Del  \\[◄/►] Month  \\[/] Search  {_FOOTER_GLOBAL}",
    "reports": f"\\[c] Chart  \\[i] Inv  \\[r] Reload  {_FOOTER_GLOBAL}",
    "recurring": f"\\[a] Add  \\[e] Edit  \\[d] Del  \\[g] Generate  \\[r] Reload  {_FOOTER_GLOBAL}",
}


class _NavTab(Tab):
    """Tab that never receives keyboard focus."""

    ALLOW_FOCUS = False


class _NavTabs(Tabs):
    """Tab bar that never receives keyboard focus and ignores arrow keys."""

    ALLOW_FOCUS = False

    def action_previous_tab(self) -> None:
        """Disable arrow-key tab switching."""

    def action_next_tab(self) -> None:
        """Disable arrow-key tab switching."""


class HledgerTuiApp(App):
    """A TUI for managing hledger journal transactions."""

    TITLE = "hledger-textual"
    CSS_PATH = "styles/app.tcss"

    BINDINGS = [
        Binding("1", "switch_section('summary')", "Summary", show=False),
        Binding("2", "switch_section('transactions')", "Transactions", show=False),
        Binding("3", "switch_section('recurring')", "Recurring", show=False),
        Binding("4", "switch_section('budget')", "Budget", show=False),
        Binding("5", "switch_section('reports')", "Reports", show=False),
        Binding("6", "switch_section('accounts')", "Accounts", show=False),
        Binding("i", "show_about", "About", show=False),
        Binding("s", "git_sync", "Sync", show=False),
        Binding("question_mark", "show_help", "Help", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, journal_file: Path) -> None:
        """Initialize the app.

        Args:
            journal_file: Path to the hledger journal file.
        """
        super().__init__()
        self.journal_file = journal_file
        saved_theme = load_theme()
        if saved_theme:
            self.theme = saved_theme

    def compose(self) -> ComposeResult:
        """Create the app layout."""
        yield _NavTabs(
            _NavTab("1. Summary", id="tab-summary"),
            _NavTab("2. Transactions", id="tab-transactions"),
            _NavTab("3. Recurring", id="tab-recurring"),
            _NavTab("4. Budget", id="tab-budget"),
            _NavTab("5. Reports", id="tab-reports"),
            _NavTab("6. Accounts", id="tab-accounts"),
            id="nav-tabs",
        )

        with ContentSwitcher(initial="summary", id="content-switcher"):
            yield SummaryPane(self.journal_file, id="summary")
            yield TransactionsPane(self.journal_file, id="transactions")
            yield BudgetPane(self.journal_file, id="budget")
            yield ReportsPane(self.journal_file, id="reports")
            yield AccountsPane(self.journal_file, id="accounts")
            yield RecurringPane(self.journal_file, id="recurring")

        yield Static(_FOOTER_COMMANDS["summary"], id="footer-bar")

    def on_mount(self) -> None:
        """Focus the default section after mount."""
        self._focus_section("summary")
        self._check_for_updates()
        if load_auto_generate_recurring():
            self._auto_generate_recurring()

    @work(thread=True, exclusive=True, group="startup-update-check")
    def _check_for_updates(self) -> None:
        """Check PyPI for a newer version and notify once if found."""
        import importlib.metadata

        from hledger_textual.updates import get_latest_version, is_newer

        try:
            meta = importlib.metadata.metadata("hledger-textual")
            current = meta.get("Version", "0")
        except importlib.metadata.PackageNotFoundError:
            return

        latest = get_latest_version()
        if latest and is_newer(latest, current):
            self.app.call_from_thread(
                self.notify,
                f"hledger-textual {latest} is available (current: {current})",
                severity="information",
                timeout=8,
            )

    @work(thread=True, exclusive=True, group="startup-auto-generate")
    def _auto_generate_recurring(self) -> None:
        """Auto-generate pending recurring transactions for the current month on startup."""
        from datetime import date

        from hledger_textual.recurring import (
            RecurringError,
            compute_pending,
            ensure_recurring_file,
            generate_transactions,
            parse_recurring_rules,
        )

        try:
            recurring_path = ensure_recurring_file(self.journal_file)
            rules = parse_recurring_rules(recurring_path)
        except Exception:
            return

        today = date.today()
        pending: list[tuple] = []
        for rule in rules:
            try:
                dates = compute_pending(rule, self.journal_file, today)
            except Exception:
                continue
            if dates:
                pending.append((rule, dates))

        if not pending:
            return

        for rule, dates in pending:
            try:
                generate_transactions(rule, dates, self.journal_file)
            except RecurringError:
                return

        total = sum(len(d) for _, d in pending)
        self.app.call_from_thread(
            self.notify,
            f"Auto-generated {total} recurring transaction(s)",
            severity="information",
            timeout=5,
        )
        self.app.call_from_thread(self._refresh_all_panes)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab activation (click) — switch content and focus."""
        if not event.tab or not event.tab.id:
            return
        section = event.tab.id.removeprefix("tab-")
        self.query_one("#content-switcher", ContentSwitcher).current = section
        self.query_one("#footer-bar", Static).update(
            _FOOTER_COMMANDS.get(section, "")
        )
        self._focus_section(section)

    def _activate_section(self, section: str) -> None:
        """Set the active tab — triggers on_tabs_tab_activated."""
        self.query_one("#nav-tabs", _NavTabs).active = f"tab-{section}"

    def _focus_section(self, section: str) -> None:
        """Move keyboard focus to the main widget in the given section."""
        if section == "summary":
            self.query_one("#summary-breakdown-table", DataTable).focus()
        elif section == "transactions":
            self.query_one(TransactionsTable).query_one(DataTable).focus()
        elif section == "accounts":
            self.query_one("#accounts-table", DataTable).focus()
        elif section == "budget":
            self.query_one("#budget-table", DataTable).focus()
        elif section == "reports":
            self.query_one("#reports-table", DataTable).focus()
        elif section == "recurring":
            self.query_one("#recurring-table", DataTable).focus()

    def _refresh_all_panes(self) -> None:
        """Silently reload every data pane after any journal mutation."""
        summary = self.query_one(SummaryPane)
        summary._load_static_data()
        summary._load_breakdown_data()
        self.query_one(TransactionsPane).reload()
        self.query_one(AccountsPane)._load_data()
        self.query_one(BudgetPane)._load_budget_data()
        self.query_one(ReportsPane)._load_report_data()

    def on_transactions_table_journal_changed(
        self, event: TransactionsTable.JournalChanged
    ) -> None:
        """Silently refresh all data panes after a journal mutation."""
        self._refresh_all_panes()

    def on_recurring_pane_journal_changed(
        self, event: RecurringPane.JournalChanged
    ) -> None:
        """Silently refresh all data panes after recurring transactions are generated."""
        self._refresh_all_panes()

    def action_switch_section(self, section: str) -> None:
        """Switch to the given section via keyboard shortcut (1-6)."""
        self._activate_section(section)

    def action_show_about(self) -> None:
        """Open the about modal with journal and app information."""
        from hledger_textual.screens.about import AboutModal

        self.push_screen(AboutModal(self.journal_file))

    def action_show_help(self) -> None:
        """Open the keyboard shortcuts help panel."""
        from hledger_textual.screens.help import HelpScreen

        self.push_screen(HelpScreen())

    def action_git_sync(self) -> None:
        """Show confirmation dialog, then commit + pull + push via git."""
        from hledger_textual.git import is_git_repo
        from hledger_textual.screens.sync_confirm import SyncConfirmModal

        if not is_git_repo(self.journal_file):
            self.notify("Not a git repository", severity="warning")
            return

        def on_confirm(confirmed: bool | None) -> None:
            if confirmed:
                self._run_git_sync()

        self.push_screen(SyncConfirmModal(), callback=on_confirm)

    @work(thread=True, exclusive=True, group="git-sync")
    def _run_git_sync(self) -> None:
        """Execute the git sync in a background thread."""
        from hledger_textual.git import GitError, git_sync

        self.app.call_from_thread(
            self.notify, "Syncing...", severity="information"
        )
        try:
            result = git_sync(self.journal_file)
            self.app.call_from_thread(
                self.notify, result, severity="information"
            )
        except GitError as exc:
            self.app.call_from_thread(
                self.notify, str(exc), severity="error"
            )
