"""Export table data to CSV and PDF formats."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class ExportData:
    """Container for data to be exported from a pane.

    Attributes:
        title: Human-readable title for the export (e.g. "Transactions March 2026").
        headers: Column header names.
        rows: List of rows, each a list of string cell values.
        pane_name: Short pane identifier used in default filenames.
    """

    title: str
    headers: list[str]
    rows: list[list[str]]
    pane_name: str


def default_export_dir() -> Path:
    """Return the default export directory, creating it if needed.

    Returns:
        Path to ~/Documents/hledger-exports/.
    """
    export_dir = Path.home() / "Documents" / "hledger-exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def default_filename(pane_name: str, fmt: str) -> str:
    """Generate a default filename for an export.

    Args:
        pane_name: Short pane identifier (e.g. "transactions").
        fmt: File format extension ("csv" or "pdf").

    Returns:
        A filename like "transactions_2026-03-13.csv".
    """
    today = date.today().isoformat()
    return f"{pane_name}_{today}.{fmt}"


def export_csv(data: ExportData, path: Path) -> None:
    """Export data to a CSV file.

    Args:
        data: The export data containing headers and rows.
        path: Destination file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(data.headers)
        writer.writerows(data.rows)


def export_pdf(data: ExportData, path: Path) -> None:
    """Export data to a PDF file.

    Uses fpdf2 with A4 landscape for wide tables (>4 columns),
    portrait for narrow ones. Includes a title line and bold header row.

    Args:
        data: The export data containing headers and rows.
        path: Destination file path.
    """
    from fpdf import FPDF

    path.parent.mkdir(parents=True, exist_ok=True)

    orientation = "L" if len(data.headers) > 4 else "P"
    pdf = FPDF(orientation=orientation, unit="mm", format="A4")
    # Use cp1252 encoding for currency symbol support (€, £, ¥)
    pdf.core_fonts_encoding = "cp1252"
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, data.title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Calculate column widths based on available page width
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    n_cols = len(data.headers)
    col_width = page_width / n_cols if n_cols else page_width

    # Header row
    pdf.set_font("Helvetica", "B", 9)
    for header in data.headers:
        pdf.cell(col_width, 7, header, border=1)
    pdf.ln()

    # Data rows
    pdf.set_font("Helvetica", size=8)
    for row in data.rows:
        for i, cell in enumerate(row):
            # Strip any Rich markup
            clean = _strip_markup(cell)
            pdf.cell(col_width, 6, clean, border=0)
        pdf.ln()

    pdf.output(str(path))


def _strip_markup(text: str) -> str:
    """Remove Rich/Textual markup tags from a string.

    Args:
        text: Text potentially containing [bold], [red], etc.

    Returns:
        Plain text with markup tags removed.
    """
    import re

    return re.sub(r"\[/?[a-zA-Z_ ]+\]", "", text)
