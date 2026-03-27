"""Modal screen showing a financial report chart in full-screen dialog."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Label
from textual.containers import Vertical

from hledger_textual.widgets.report_chart import ReportChart


class ReportChartModal(ModalScreen[None]):
    """Modal dialog displaying a chart for the current financial report."""

    BINDINGS = [
        Binding("escape,c", "dismiss_screen", "Close", show=True),
    ]

    def __init__(self, chart_data: dict, report_type: str, title: str) -> None:
        """Initialise the modal.

        Args:
            chart_data: Pre-computed chart data from ``extract_chart_data``.
            report_type: One of ``"is"``, ``"bs"``, or ``"cf"``.
            title: Human-readable label shown at the top of the dialog.
        """
        super().__init__()
        self._chart_data = chart_data
        self._report_type = report_type
        self._title = title

    def compose(self) -> ComposeResult:
        """Create the dialog layout."""
        with Vertical(id="report-chart-dialog"):
            yield Label(self._title, id="report-chart-modal-title")
            yield ReportChart(id="report-chart-modal-plot")

    def on_mount(self) -> None:
        """Render the chart once the widget is attached."""
        chart = self.query_one("#report-chart-modal-plot", ReportChart)
        chart.replot(self._chart_data, self._report_type)

    def action_dismiss_screen(self) -> None:
        """Close the modal."""
        self.dismiss(None)
